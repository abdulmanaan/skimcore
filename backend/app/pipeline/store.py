from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Channel, Video
from app.models import Transcript


async def upsert_channel(
    session: AsyncSession, youtube_channel_id: str, data: dict
) -> Channel:
    """Insert the channel, or update it if it already exists."""
    result = await session.execute(
        select(Channel).where(Channel.youtube_channel_id == youtube_channel_id)
    )
    channel = result.scalar_one_or_none()

    if channel is None:
        channel = Channel(youtube_channel_id=youtube_channel_id, **data)
        session.add(channel)
    else:
        for key, value in data.items():
            setattr(channel, key, value)

    await session.flush()
    return channel


async def upsert_video(
    session: AsyncSession, channel: Channel, data: dict
) -> Video:
    """Insert the video, or update it if it already exists."""
    youtube_video_id = data.pop("youtube_video_id")
    result = await session.execute(
        select(Video).where(Video.youtube_video_id == youtube_video_id)
    )
    video = result.scalar_one_or_none()

    if video is None:
        video = Video(
            youtube_video_id=youtube_video_id,
            channel_id=channel.id,
            **data,
        )
        session.add(video)
    else:
        for key, value in data.items():
            setattr(video, key, value)

    await session.flush()
    return video


async def upsert_transcript(
    session: AsyncSession, video: Video, data: dict
) -> Transcript:
    """Insert the transcript, or replace it if one already exists."""
    result = await session.execute(
        select(Transcript).where(Transcript.video_id == video.id)
    )
    transcript = result.scalar_one_or_none()

    if transcript is None:
        transcript = Transcript(video_id=video.id, **data)
        session.add(transcript)
    else:
        transcript.language = data["language"]
        transcript.segments = data["segments"]

    await session.flush()
    return transcript