import asyncio
from app.core.db import AsyncSessionLocal
from app.pipeline.store import upsert_channel, upsert_video
from app.pipeline.youtube import fetch_channels, fetch_videos, search_videos


async def ingest_topic(query: str, limit: int = 10) -> None:
    """Search a topic, fetch details, and store videos and channels."""
    video_ids = await search_videos(query, limit=limit)
    if not video_ids:
        print("No videos found.")
        return

    videos = await fetch_videos(video_ids)
    channel_ids = list({v["youtube_channel_id"] for v in videos})
    channels = await fetch_channels(channel_ids)

    async with AsyncSessionLocal() as session:
        for v in videos:
            data = dict(v)
            cid = data.pop("youtube_channel_id")
            data.pop("channel_title")

            channel_data = channels.get(cid)
            if channel_data is None:
                continue

            channel = await upsert_channel(session, cid, channel_data)
            await upsert_video(session, channel, data)

        await session.commit()

    print(f"Stored {len(videos)} videos for '{query}'.")


if __name__ == "__main__":
    import sys

    topic = sys.argv[1] if len(sys.argv) > 1 else "critical thinking"
    asyncio.run(ingest_topic(topic))
