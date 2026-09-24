import httpx
from app.core.config import settings
import re
from datetime import datetime

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


def _parse_duration(iso: str) -> int:
    """Convert ISO 8601 duration (e.g. PT12M30S) to seconds."""
    match = re.fullmatch(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso
    )
    if not match:
        return 0
    hours, minutes, seconds = (int(g or 0) for g in match.groups())
    return hours * 3600 + minutes * 60 + seconds


async def fetch_videos(video_ids: list[str]) -> list[dict]:
    """Fetch full details for up to 50 videos in one call."""
    params = {
        "key": settings.YOUTUBE_API_KEY,
        "part": "snippet,contentDetails",
        "id": ",".join(video_ids),
        "maxResults": 50,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(f"{BASE}/videos", params=params)
        r.raise_for_status()
        data = r.json()

    videos = []
    for item in data.get("items", []):
        snippet = item["snippet"]
        thumbs = snippet["thumbnails"]
        best = thumbs.get("maxres") or thumbs.get("high") or thumbs["medium"]
        videos.append({
            "youtube_video_id": item["id"],
            "youtube_channel_id": snippet["channelId"],
            "channel_title": snippet["channelTitle"],
            "title": snippet["title"],
            "thumbnail_url": best["url"],
            "duration_seconds": _parse_duration(item["contentDetails"]["duration"]),
            "published_at": datetime.fromisoformat(snippet["publishedAt"]),
        })
    return videos


async def fetch_channels(channel_ids: list[str]) -> dict[str, dict]:
    """Fetch channel logo and subscriber count, keyed by channel id."""
    params = {
        "key": settings.YOUTUBE_API_KEY,
        "part": "snippet,statistics",
        "id": ",".join(channel_ids),
        "maxResults": 50,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(f"{BASE}/channels", params=params)
        r.raise_for_status()
        data = r.json()

    result = {}
    for item in data.get("items", []):
        stats = item.get("statistics", {})
        subs = stats.get("subscriberCount")
        result[item["id"]] = {
            "title": item["snippet"]["title"],
            "logo_url": item["snippet"]["thumbnails"]["default"]["url"],
            "subscriber_count": int(subs) if subs else None,
        }
    return result
