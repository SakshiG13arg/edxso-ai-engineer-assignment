from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Influencer(BaseModel):
    influencer_id: str
    name: str
    handle: str
    platform: str
    profile_url: str
    followers: int
    engagement_rate: Optional[float] = None
    niche: str
    content_themes: str
    contact_email: str = "Not Found"
    website: str = "Not Found"
    audience_age: str = "Not Available"
    audience_gender: str = "Not Available"
    audience_geography: str = "India"
    source: str
    source_date: str
    source_url: str
    recent_content_signal: str = "Not available from discovery source"

class FilterResult(BaseModel):
    influencer_id: str
    passed: bool
    reason: str
    score: float = Field(ge=0, le=100)

class MessageSet(BaseModel):
    email_subject: str
    email_body: str
    instagram_dm: str
    personalization_signals: list[str]
    quality_flags: list[str] = []

class OutreachRecord(BaseModel):
    influencer_id: str
    channel: str
    message_generated: bool
    sent: bool
    sent_at: Optional[datetime] = None
    status: str
    error: Optional[str] = None
