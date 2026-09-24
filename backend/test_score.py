import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.db import AsyncSessionLocal
from app.models import Video
from app.pipeline.scoring import score_transcript, signal_score


async def main() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Video).options(selectinload(Video.transcript)).limit(10)
        )
        for video in result.scalars():
            if video.transcript is None:
                continue
            parts = score_transcript(
                video.transcript.segments, video.duration_seconds
            )
            score = signal_score(parts, video.duration_seconds)
            print(f"{score:5.1f}  {video.title[:55]}")
            print(f"        {parts}")


asyncio.run(main())
