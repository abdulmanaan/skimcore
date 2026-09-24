from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Channel, Video, Transcript, Analysis, Topic, TopicVideo


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


async def upsert_analysis(
    session: AsyncSession, video: Video, parts: dict, score: float
) -> Analysis:
    """Insert or update the score portion of a video's analysis."""
    result = await session.execute(
        select(Analysis).where(Analysis.video_id == video.id)
    )
    analysis = result.scalar_one_or_none()

    if analysis is None:
        analysis = Analysis(video_id=video.id, signal_score=score, **parts)
        session.add(analysis)
    else:
        analysis.signal_score = score
        for key, value in parts.items():
            setattr(analysis, key, value)

    await session.flush()
    return analysis


async def get_or_create_topic(session: AsyncSession, name: str) -> Topic:
    """Find a topic by slug, or create it."""
    slug = "-".join(name.lower().split())
    result = await session.execute(select(Topic).where(Topic.slug == slug))
    topic = result.scalar_one_or_none()

    if topic is None:
        topic = Topic(name=name.strip(), slug=slug)
        session.add(topic)
        await session.flush()
    return topic


async def rebuild_ranks(session: AsyncSession, topic: Topic) -> None:
    """Re-rank a topic's videos by signal score, best first."""
    await session.execute(
        delete(TopicVideo).where(TopicVideo.topic_id == topic.id)
    )

    result = await session.execute(
        select(Video.id)
        .join(Analysis, Analysis.video_id == Video.id)
        .order_by(Analysis.signal_score.desc())
    )
    for rank, video_id in enumerate(result.scalars(), start=1):
        session.add(
            TopicVideo(topic_id=topic.id, video_id=video_id, rank=rank)
        )
