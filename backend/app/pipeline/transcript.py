import asyncio
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

_api = YouTubeTranscriptApi()


def _fetch_sync(youtube_video_id: str) -> dict | None:
    """Fetch an English transcript for one video. Blocking."""
    try:
        fetched = _api.fetch(youtube_video_id, languages=["en", "en-US", "en-GB"])
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
        return None

    segments = [
        {"start": round(s.start, 2), "text": s.text.strip()}
        for s in fetched.snippets
        if s.text.strip()
    ]
    if not segments:
        return None

    return {"language": fetched.language_code, "segments": segments}


async def fetch_transcript(youtube_video_id: str) -> dict | None:
    """Fetch a transcript without blocking the event loop."""
    return await asyncio.to_thread(_fetch_sync, youtube_video_id)
