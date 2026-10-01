# Architecture

```text
                 ┌───────────────────────┐
                 │ Discovery adapters    │
                 │ Seed CSV / YouTube    │
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │ Normalization          │
                 │ schema + validation    │
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │ Filtering / scoring    │
                 │ transparent reasons   │
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │ Enrichment             │
                 │ public email only      │
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │ LLM personalization    │
                 │ Email + Instagram DM   │
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │ Human review            │
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │ Sending layer          │
                 │ SMTP dry-run / manual  │
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │ SQLite outreach log    │
                 │ duplicate constraint  │
                 └───────────────────────┘
```

## Design decisions

### Adapter pattern
Discovery is isolated behind `SeedDiscovery` and `YouTubeDiscovery`, allowing another source to be added without changing filtering or personalization.

### Data integrity
Source values are preserved and labelled. Missing emails are not inferred.

### Human-in-the-loop
The system generates messages but does not automatically send Instagram DMs. Email sending defaults to dry-run.

### Idempotency
The database has a unique key on influencer + channel + campaign, preventing duplicate outreach.

### LLM safety
The prompt explicitly restricts the model to supplied facts and asks it not to invent recent posts or audience details. Message length is checked after generation.

### Scale path
For 500+ creators, use PostgreSQL, queue workers, provider-specific rate limiting, caching and batch LLM calls.
