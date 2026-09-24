import httpx
from app.core.config import settings

BASE = "https://www.googleapis.com/youtube/v3"


async def search_videos(query: str, limit: int = 10) -> list[str]:
    """Search videos by topics and return only their ids."""
    params = {
        "key": settings.YOUTUBE_API_KEY,
        "part": "id",
        "q": query,
        "type": "video",
        "videoDuration": "medium",
        "videoCaption": "closedCaption",
        "relevanceLanguage": "en",
        "maxResults": limit,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(f"{BASE}/search", params=params)
        r.raise_for_status()
        data = r.json()

    return [item["id"]["videoId"] for item in data.get("items", [])]
