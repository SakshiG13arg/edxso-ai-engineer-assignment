from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from .config import SETTINGS, OUTPUT_DIR
from .discovery import SeedDiscovery, YouTubeDiscovery
from .enrichment import enrich
from .filtering import filter_influencers
from .personalization import personalize
from .db import OutreachDB


def run(source="seed", query="technology gadgets India", target=50):
    if source == "youtube":
        import os
        discovery = YouTubeDiscovery(os.getenv("YOUTUBE_API_KEY", ""), os.getenv("YOUTUBE_REGION", "IN"))
        discovered = discovery.discover(query, target)
    else:
        discovery = SeedDiscovery(SETTINGS["runtime"]["seed_file"])
        discovered = discovery.discover(target)
    discovered = enrich(discovered)
    discovered.to_csv(OUTPUT_DIR / "discovered_influencers.csv", index=False)
    filtered, shortlist = filter_influencers(discovered)
    filtered.to_csv(OUTPUT_DIR / "filtered_influencers.csv", index=False)
    messages = personalize(shortlist)
    messages.to_csv(OUTPUT_DIR / "personalized_messages.csv", index=False)
    db = OutreachDB(SETTINGS["runtime"]["db_file"])
    tracker = []
    for _, row in shortlist.iterrows():
        msg = messages[messages.influencer_id == row.influencer_id].iloc[0].to_dict()
        tracker.append({
            "Influencer": row["name"], "Email": row["contact_email"], "Message Generated": True,
            "Sent": False, "Date": "", "Status": "READY_FOR_REVIEW"
        })
    pd.DataFrame(tracker).to_csv(OUTPUT_DIR / "outreach_tracker.csv", index=False)
    summary = {"source": source, "discovered": len(discovered), "shortlisted": len(shortlist), "messages_generated": len(messages), "emails_found": int((discovered.contact_email != "Not Found").sum())}
    (OUTPUT_DIR / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
