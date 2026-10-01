from __future__ import annotations
import re
import pandas as pd
from .config import SETTINGS


def _text_relevant(row) -> bool:
    blob = " ".join(str(row.get(c, "")) for c in ["name", "handle", "niche", "content_themes"]).lower()
    keywords = SETTINGS["filter"]["required_keywords"]
    return any(re.search(rf"\b{re.escape(k)}\b", blob) for k in keywords)


def filter_influencers(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cfg = SETTINGS["filter"]
    results = []
    for _, row in df.iterrows():
        followers = int(row.get("followers", 0) or 0)
        er = row.get("engagement_rate")
        er_ok = pd.notna(er) and float(er) >= cfg["min_engagement_rate"]
        micro_ok = cfg["min_followers"] <= followers <= cfg["max_followers"]
        niche_ok = _text_relevant(row)
        passed = micro_ok and er_ok and niche_ok
        reasons = []
        reasons.append("micro range" if micro_ok else "outside micro range")
        reasons.append("engagement threshold" if er_ok else "engagement below threshold/missing")
        reasons.append("technology relevance" if niche_ok else "technology relevance not established")
        score = min(100, (min(followers / cfg["max_followers"], 1) * 30) + (min(float(er or 0) / 10, 1) * 40) + (30 if niche_ok else 0))
        results.append({"influencer_id": row["influencer_id"], "passed": passed, "reason": ("PASS: " if passed else "FAIL: ") + " + ".join(reasons), "score": round(score, 2)})
    res = pd.DataFrame(results)
    merged = df.merge(res, on="influencer_id", how="left")
    return merged, merged[merged["passed"]].copy()
