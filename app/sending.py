from __future__ import annotations
import os
import smtplib
from email.message import EmailMessage
from .config import SETTINGS
from .db import OutreachDB


def send_email(influencer: dict, message: dict, db: OutreachDB, dry_run=True):
    email = influencer.get("contact_email", "Not Found")
    if email == "Not Found":
        return db.record(influencer["influencer_id"], "email", SETTINGS["project"]["campaign_id"], True, False, "SKIPPED_NO_EMAIL")
    if dry_run:
        return db.record(influencer["influencer_id"], "email", SETTINGS["project"]["campaign_id"], True, False, "SIMULATED_SEND")
    msg = EmailMessage()
    msg["From"] = os.environ["SMTP_FROM"]
    msg["To"] = email
    msg["Subject"] = message["email_subject"]
    msg.set_content(message["email_body"])
    try:
        with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", 587)), timeout=20) as smtp:
            smtp.starttls(); smtp.login(os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"]); smtp.send_message(msg)
        return db.record(influencer["influencer_id"], "email", SETTINGS["project"]["campaign_id"], True, True, "SENT")
    except Exception as e:
        return db.record(influencer["influencer_id"], "email", SETTINGS["project"]["campaign_id"], True, False, "SEND_ERROR", str(e))


def simulate_instagram_dm(influencer: dict, message: dict, db: OutreachDB):
    return db.record(influencer["influencer_id"], "instagram_dm", SETTINGS["project"]["campaign_id"], True, False, "MANUAL_REVIEW_REQUIRED")
