from __future__ import annotations
from fastapi import FastAPI, HTTPException
import pandas as pd
from .config import OUTPUT_DIR, SETTINGS
from .db import OutreachDB
from .workflow import run
from .personalization import personalize
from .sending import send_email

app = FastAPI(title="EDXSO Influencer Outreach API", version="1.0.0")

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/influencers")
def influencers():
    p = OUTPUT_DIR / "discovered_influencers.csv"
    if not p.exists(): run()
    return pd.read_csv(p).fillna("").to_dict(orient="records")

@app.get("/shortlist")
def shortlist():
    p = OUTPUT_DIR / "filtered_influencers.csv"
    if not p.exists(): run()
    df = pd.read_csv(p)
    return df[df["passed"] == True].fillna("").to_dict(orient="records")

@app.get("/outreach")
def outreach():
    db = OutreachDB(SETTINGS["runtime"]["db_file"])
    return [dict(zip(["id","influencer_id","channel","campaign_id","message_generated","sent","sent_at","status","error"], r)) for r in db.all()]


@app.post("/personalize/{influencer_id}")
def personalize_one(influencer_id: str):
    p = OUTPUT_DIR / "filtered_influencers.csv"
    if not p.exists(): run()
    df = pd.read_csv(p)
    row = df[df["influencer_id"] == influencer_id]
    if row.empty: raise HTTPException(404, "Influencer not found")
    return personalize(row).fillna("").to_dict(orient="records")[0]

@app.post("/send/{influencer_id}")
def send_one(influencer_id: str):
    ip = OUTPUT_DIR / "filtered_influencers.csv"
    mp = OUTPUT_DIR / "personalized_messages.csv"
    if not ip.exists() or not mp.exists(): run()
    inf_df = pd.read_csv(ip); msg_df = pd.read_csv(mp)
    inf = inf_df[inf_df["influencer_id"] == influencer_id]
    msg = msg_df[msg_df["influencer_id"] == influencer_id]
    if inf.empty or msg.empty: raise HTTPException(404, "Influencer or message not found")
    db = OutreachDB(SETTINGS["runtime"]["db_file"])
    return send_email(inf.iloc[0].to_dict(), msg.iloc[0].to_dict(), db, dry_run=True)
