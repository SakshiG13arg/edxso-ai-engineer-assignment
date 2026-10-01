# EDXSO AI Engineer Intern — Assignment 1

## Automated Micro-Influencer Outreach System

A modular Python prototype implementing:

**Discovery → Collection → Filtering → Enrichment → AI Personalization → Review → Sending Simulation → Tracking**

### Assignment coverage

| Requirement | Implementation |
|---|---|
| 50+ discovered influencers | `data/influencers_seed.csv` contains 55 public creator records |
| Micro-influencer definition | 5,000–100,000 followers configurable in `config/settings.yaml` |
| Filtering/classification | `app/filtering.py`: follower range + engagement + technology relevance |
| Profile enrichment | source URL, profile URL, contact status, content context |
| Missing email handling | never guessed; stored as `Not Found` |
| Personalized email | LLM provider with structured JSON output + deterministic fallback |
| Personalized Instagram DM | LLM provider + deterministic fallback |
| Sending layer | SMTP dry-run / simulation; duplicate prevention in SQLite |
| Outreach tracker | SQLite database + CSV export |
| UI | Streamlit dashboard |
| Backend API | FastAPI endpoints for discovery/filtering/personalization/tracking |
| Scalability | adapters, batching, SQLite abstraction, configurable limits |
| Documentation | this README + `docs/ARCHITECTURE.md` |

## Important data-integrity note

The included seed dataset is a **public-source test fixture**, not claimed to be live. Follower and engagement figures are preserved from the cited public ranking and carry a source/date field. Contact emails are `Not Found` unless a public, attributable email is supplied by a permitted enrichment source. The application never generates or guesses email addresses.

The included source is StarNgage's public India Technology ranking, which exposes creator handles, follower counts and engagement rates. The July 2026 page includes numerous accounts in the 5K–100K range. Source: https://starngage.com/plus/en-us/influencer/ranking/instagram/india/technology

For a fresh run, the project also supports the YouTube Data API v3. Google's documentation states that `search.list` can search for channels and `channels.list` can retrieve channel resources/statistics. API keys are loaded from environment variables and never committed.

## Tech stack

- Python 3.11+
- Pandas
- Pydantic
- SQLite
- FastAPI + Uvicorn
- Streamlit
- Requests
- PyYAML
- Optional OpenAI-compatible LLM provider (OpenAI or local Ollama)
- Optional YouTube Data API v3
- SMTP adapter in dry-run mode by default

## Project structure

```text
edxso_ai_engineer_assignment1/
├── app/
│   ├── api.py
│   ├── config.py
│   ├── db.py
│   ├── discovery.py
│   ├── enrichment.py
│   ├── filtering.py
│   ├── llm.py
│   ├── personalization.py
│   ├── schemas.py
│   ├── sending.py
│   ├── workflow.py
│   └── ui.py
├── config/settings.yaml
├── data/influencers_seed.csv
├── docs/ARCHITECTURE.md
├── outputs/.gitkeep
├── scripts/run_pipeline.py
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

### 1. Create environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env`.

For deterministic offline demonstration, no API key is required. The system uses the included public-source seed data and a deterministic personalization fallback.

For AI-generated messages, configure either:

- `LLM_PROVIDER=ollama` and run a local Ollama model, or
- `LLM_PROVIDER=openai` with `OPENAI_API_KEY`.

For fresh YouTube discovery, set `YOUTUBE_API_KEY`.

## Run the complete pipeline

```bash
python scripts/run_pipeline.py
```

The default seed run processes all 55 included records.

Outputs are written to `outputs/`:

- `discovered_influencers.csv`
- `filtered_influencers.csv`
- `personalized_messages.csv`
- `outreach_tracker.csv`
- `outreach.db`
- `run_summary.json`

### Generate a fresh YouTube discovery dataset

```bash
python scripts/run_pipeline.py --source youtube --query "technology gadgets India" --target 50
```

The YouTube adapter uses only the documented API. It does not scrape private data, does not bypass platform restrictions, and does not fabricate contact information.

## Run the dashboard

```bash
streamlit run app/ui.py
```

The dashboard shows:

1. discovered records
2. pass/fail reasons
3. shortlisted creators
4. generated email/DM
5. sending simulation
6. duplicate protection
7. outreach status

## Run the API

```bash
uvicorn app.api:app --reload
```

Useful endpoints:

- `GET /health`
- `GET /influencers`
- `GET /shortlist`
- `POST /personalize/{influencer_id}`
- `POST /send/{influencer_id}`
- `GET /outreach`

## Filtering logic

The demo configuration uses:

- followers: 5,000–100,000 inclusive
- minimum engagement rate: 2.0%
- niche: technology
- optional keyword relevance check

Each record receives a transparent reason such as:

- `PASS: micro range + engagement threshold + technology category`
- `FAIL: follower count above micro range`
- `FAIL: engagement below threshold`

The thresholds are configuration, not hard-coded business claims.

## Enrichment methodology

The enrichment layer follows this order:

1. preserve discovery-source data;
2. normalize profile URLs;
3. retain only publicly supplied email fields;
4. optionally query an approved enrichment provider if configured;
5. otherwise set email to `Not Found`;
6. never infer an email from a name or domain.

This deliberately follows the assignment's instruction not to guess emails.

## Personalization design

The LLM receives structured signals rather than a generic template:

- creator name/handle
- niche
- content theme
- platform
- follower count
- engagement rate
- optional recent-content signal
- collaboration angle

It must return JSON containing:

```json
{
  "email_subject": "...",
  "email_body": "60-90 words",
  "instagram_dm": "15-30 words",
  "personalization_signals": ["..."],
  "quality_flags": []
}
```

A validator rejects obviously invalid lengths and missing personalization signals. If an LLM is unavailable, a deterministic fallback produces valid demonstration messages using the actual record fields. This makes the project runnable without hiding the distinction between AI-generated and fallback content.

## Sending layer

The default mode is **dry-run**. It records what would be sent without contacting creators.

SMTP can be configured later, but the code requires:

- valid email
- generated message
- `sent_at` not already populated
- no previous successful outreach for the same influencer

Instagram is always represented as a manual/simulated workflow. The system does not bypass Meta/Instagram restrictions.

## Duplicate prevention

SQLite has a unique constraint on `(influencer_id, channel, campaign_id)`. A second send attempt returns a duplicate status rather than sending again.

## Error handling

The pipeline handles:

- missing email
- malformed CSV values
- duplicate creators
- unavailable LLM
- invalid LLM JSON
- invalid message lengths
- API errors
- missing YouTube API key
- duplicate outreach
- dry-run sending

## Scalability

The system can move from 50 to 500+ records by:

- replacing the seed CSV with API discovery;
- batching API requests;
- storing records in PostgreSQL instead of SQLite;
- adding a queue/worker layer;
- adding provider-specific enrichment adapters;
- caching API responses;
- adding rate-limit/backoff controls;
- separating review and sending permissions.

## Limitations

1. The seed dataset is a dated public-source fixture, not a live social-media crawl.
2. Public rankings may have stale or estimated metrics.
3. Instagram engagement metrics in the fixture come from the source; the system does not pretend they are freshly calculated.
4. Public contact email availability is limited; missing values remain `Not Found`.
5. Instagram DM automation is simulated to respect platform restrictions.
6. LLM output should be human-reviewed before any real outreach.

## Submission checklist

- [x] Working prototype
- [x] 50+ discovered influencer records
- [x] Filtering and pass/fail reasons
- [x] Enrichment fields
- [x] Email + Instagram DM generation
- [x] Outreach tracker
- [x] Duplicate prevention
- [x] Dry-run sending layer
- [x] API + dashboard
- [x] README and architecture documentation
- [x] `.env.example`
- [x] No fabricated emails or engagement values

## Suggested demo sequence

1. Open Streamlit dashboard.
2. Load 55 discovered records.
3. Show filtering and pass/fail reasons.
4. Open a few shortlisted creators.
5. Generate personalized email + DM.
6. Show `Not Found` email handling for creators without public contact information.
7. Click dry-run send for one record.
8. Repeat send and show duplicate prevention.
9. Open outreach tracker.
10. Explain how the YouTube adapter turns the fixture into a fresh API-driven discovery run.
