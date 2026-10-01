from __future__ import annotations
import streamlit as st
import pandas as pd
import ast
from pathlib import Path
from .config import OUTPUT_DIR
from .workflow import run

st.set_page_config(page_title="EDXSO Influencer Outreach", layout="wide")
st.title("EDXSO — Automated Micro-Influencer Outreach")
st.caption("Assignment 1 prototype | Discovery → Filtering → Enrichment → AI Personalization → Review → Tracking")

if st.button("Run complete pipeline"):
    with st.spinner("Running pipeline..."):
        summary = run()
    st.success(f"Discovered {summary['discovered']} | Shortlisted {summary['shortlisted']} | Messages {summary['messages_generated']}")

p = OUTPUT_DIR / "filtered_influencers.csv"
if not p.exists():
    st.info("Click 'Run complete pipeline' to create the demo outputs.")
    st.stop()

f = pd.read_csv(p).fillna("")
short = f[f["passed"] == True]
col1, col2, col3 = st.columns(3)
col1.metric("Discovered", len(f)); col2.metric("Shortlisted", len(short)); col3.metric("Email found", int((f.contact_email != "Not Found").sum()))

st.subheader("Filtering results")
st.dataframe(f[["name","platform","followers","engagement_rate","niche","contact_email","passed","reason"]], use_container_width=True)

m = OUTPUT_DIR / "personalized_messages.csv"
if m.exists():
    msgs = pd.read_csv(m).fillna("")
    st.subheader("Personalized outreach")
    merged = short.merge(msgs, on="influencer_id", how="left")
    for _, r in merged.head(10).iterrows():
        with st.expander(f"{r['name']} — {r['handle']}"):
            st.write("**Email subject:**", r["email_subject"])
            st.write(r["email_body"])
            st.write("**Instagram DM:**", r["instagram_dm"])
            st.caption("Signals: " + ", ".join(ast.literal_eval(r["personalization_signals"]) if isinstance(r["personalization_signals"], str) and r["personalization_signals"].startswith("[") else [str(r["personalization_signals"])]))
