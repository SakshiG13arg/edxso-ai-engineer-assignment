from __future__ import annotations
import json
import os
import re
from .config import LLM_PROVIDER
from .schemas import Influencer, MessageSet


def _fallback(inf: Influencer) -> MessageSet:
    name = inf.name.split()[0] if inf.name else inf.handle.lstrip("@").split("_")[0]
    theme = inf.content_themes or "technology content"
    email_subject = f"Collaboration idea for {name}'s {inf.niche} content"
    email_body = (
        f"Hi {name},\n\n"
        f"I came across your {inf.niche} content and liked the focus on {theme}. "
        f"Your audience size and engagement suggest a focused creator community that could be a good fit for a technology-led education collaboration. "
        f"We'd like to explore a paid UGC or sponsored-content partnership with EDXSO, with room for you to keep your own voice and format. "
        f"If this sounds relevant, I can share the campaign brief, deliverables and timelines.\n\n"
        f"Best,\nEDXSO Team"
    )
    dm = f"Hi {name}, loved your {theme} content. Would you be open to a paid EDXSO tech collaboration tailored to your audience?"
    return MessageSet(email_subject=email_subject, email_body=email_body, instagram_dm=dm, personalization_signals=[inf.niche, theme, inf.platform])


def generate(inf: Influencer) -> MessageSet:
    if LLM_PROVIDER == "fallback":
        return _fallback(inf)

    from openai import OpenAI
    if LLM_PROVIDER == "openai":
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        base_url = None
    elif LLM_PROVIDER == "ollama":
        client = OpenAI(base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"), api_key="ollama")
        model = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
        base_url = True
    else:
        return _fallback(inf)

    prompt = f"""You are an outreach copywriter. Generate genuinely personalized collaboration outreach from these factual signals only.
Creator: {inf.name} ({inf.handle})
Platform: {inf.platform}
Followers: {inf.followers}
Engagement: {inf.engagement_rate}
Niche: {inf.niche}
Content themes: {inf.content_themes}
Recent content signal: {inf.recent_content_signal}
Brand: EDXSO, an education consulting and institutional growth organization.

Return ONLY JSON with keys: email_subject, email_body, instagram_dm, personalization_signals, quality_flags.
Email body must be 60-90 words. DM must be 15-30 words. Do not invent a recent post, product, audience demographic, or contact detail. If recent content is unavailable, personalize from the available niche/theme signals.
"""
    resp = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], temperature=0.7, response_format={"type": "json_object"})
    data = json.loads(resp.choices[0].message.content)
    msg = MessageSet(**data)
    ew = len(re.findall(r"\b\w+[\w'-]*\b", msg.email_body))
    dw = len(re.findall(r"\b\w+[\w'-]*\b", msg.instagram_dm))
    flags = list(msg.quality_flags)
    if not (60 <= ew <= 90): flags.append(f"email_word_count={ew}")
    if not (15 <= dw <= 30): flags.append(f"dm_word_count={dw}")
    return MessageSet(**{**msg.model_dump(), "quality_flags": flags})
