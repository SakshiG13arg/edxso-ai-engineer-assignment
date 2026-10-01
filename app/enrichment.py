from __future__ import annotations
import re
import pandas as pd

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def enrich(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["contact_email"] = out["contact_email"].fillna("Not Found").astype(str)
    out.loc[~out["contact_email"].str.match(EMAIL_RE), "contact_email"] = "Not Found"
    out["profile_url"] = out.apply(lambda r: r["profile_url"] if str(r["profile_url"]).startswith("http") else "Not Found", axis=1)
    out["content_themes"] = out["content_themes"].fillna("Technology")
    out["enrichment_status"] = out["contact_email"].apply(lambda x: "Email found" if x != "Not Found" else "Email Not Found")
    return out
