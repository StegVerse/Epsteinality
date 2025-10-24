# FREE-DOM (Canonical) — Epsteinality

**FREE-DOM = Factually Recounted Epstein Era — Destruction Of Morality**

This folder is the **canonical home** for FREE-DOM events. Other biographies (Trumpality, Maxwellality, etc.)
must reference these events by `event_id` instead of duplicating data.

## Files
- `events.csv` — the master event list
- `event_participants.csv` — who is involved and in what role
- `entities.csv` — base entities referenced by events

## CSV Schemas
### events.csv
- `event_id` — unique ID, e.g. `FREEDOM-0001`
- `event_date` — ISO date `YYYY-MM-DD` (or `YYYY-MM` if day unknown)
- `event_type` — one of: conviction | filing | deposition | flight | photo | settlement | press_release | other
- `title` — short title of the event
- `summary` — 1–2 line description
- `primary_source_url` — link to a verifiable primary document (court/DOJ/official)
- `secondary_sources` — comma-separated reputable links that cite primaries
- `proof_type` — court_document | official_release | scanned_record | investigative_with_primary_refs
- `tags` — comma-separated tags

### event_participants.csv
- `event_id` — must match an ID in `events.csv`
- `entity_id` — must match an ID in `entities.csv`
- `role` — principal | mentioned | appears_on_record | alleged_by_source
- `source_url` — verification link (prefer primary)
- `notes` — short context

### entities.csv
- `entity_id` — unique entity key
- `label` — display name
- `type` — person | org | venue | other
- `source_url` — authoritative link

## Example Rows (paste into the CSVs as you verify sources)

### Example `events.csv`
```
FREEDOM-0001,2008-06-30,conviction,Epstein Florida plea and conviction,Disposition and sentencing details,PRIMARY_DOC_URL,SECONDARY_URLS, court_document,conviction,florida
FREEDOM-0002,2019-07-06,filing,SDNY unsealed indictment against Epstein,US Attorney SDNY press release,DOJ_PRESS_RELEASE_URL,REPUTABLE_REPORTS, official_release,indictment,sdny
```

### Example `event_participants.csv`
```
FREEDOM-0001,e_epstein,principal,PRIMARY_DOC_URL,Named defendant
FREEDOM-0002,e_maxwell,mentioned,REPUTABLE_REPORT_URL,Mentioned in context (not a party)
```

### Example `entities.csv`
(Already provided with `e_epstein`, `e_maxwell`, `e_trump` — add more as needed)
