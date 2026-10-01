from __future__ import annotations
import re
from pathlib import Path
import pandas as pd
import requests
from .config import ROOT

class SeedDiscovery:
    def __init__(self, path: str | Path):
        self.path = ROOT / path if not Path(path).is_absolute() else Path(path)

    def discover(self, target: int = 50) -> pd.DataFrame:
        df = pd.read_csv(self.path)
        return df.head(max(target, 50)).copy()

class YouTubeDiscovery:
    ENDPOINT = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str, region: str = "IN"):
        self.api_key = api_key
        self.region = region

    def _get(self, path: str, params: dict):
        params = {**params, "key": self.api_key}
        r = requests.get(f"{self.ENDPOINT}/{path}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def discover(self, query: str, target: int = 50) -> pd.DataFrame:
        if not self.api_key:
            raise RuntimeError("YOUTUBE_API_KEY is required for YouTube discovery.")
        ids, seen = [], set()
        token = None
        while len(ids) < target and len(ids) < 250:
            params = {
                "part": "snippet",
                "q": query,
                "type": "channel",
                "maxResults": min(50, target),
                "regionCode": self.region,
            }
            if token:
                params["pageToken"] = token
            data = self._get("search", params)
            for item in data.get("items", []):
                cid = item.get("id", {}).get("channelId")
                if cid and cid not in seen:
                    seen.add(cid); ids.append(cid)
            token = data.get("nextPageToken")
            if not token: break

        rows = []
        for start in range(0, len(ids), 50):
            batch = ids[start:start+50]
            data = self._get("channels", {"part": "snippet,statistics", "id": ",".join(batch)})
            for item in data.get("items", []):
                stats = item.get("statistics", {})
                snippet = item.get("snippet", {})
                rows.append({
                    "influencer_id": f"yt_{item['id']}",
                    "name": snippet.get("title", "Unknown"),
                    "handle": snippet.get("customUrl", item["id"]),
                    "platform": "YouTube",
                    "profile_url": f"https://www.youtube.com/channel/{item['id']}",
                    "followers": int(stats.get("subscriberCount", 0)),
                    "engagement_rate": None,
                    "niche": "Technology",
                    "content_themes": snippet.get("description", "Technology creator"),
                    "contact_email": "Not Found",
                    "website": "Not Found",
                    "audience_age": "Not Available",
                    "audience_gender": "Not Available",
                    "audience_geography": self.region,
                    "source": "YouTube Data API v3",
                    "source_date": pd.Timestamp.utcnow().date().isoformat(),
                    "source_url": "https://developers.google.com/youtube/v3/docs",
                    "recent_content_signal": "Channel description only; recent-video enrichment can be added",
                })
        return pd.DataFrame(rows).head(target)
