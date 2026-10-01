from __future__ import annotations
import pandas as pd
from .llm import generate
from .schemas import Influencer


def personalize(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        inf = Influencer(**{k: row[k] for k in Influencer.model_fields if k in row.index})
        msg = generate(inf)
        rows.append({"influencer_id": inf.influencer_id, **msg.model_dump()})
    return pd.DataFrame(rows)
