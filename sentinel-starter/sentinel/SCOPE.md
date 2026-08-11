# Sentinel — Semester 1 Scope Document

**Course:** Fundamentals of Data Engineering
**Deliverable:** A complete, independently-gradable data validation platform.

## 1. Problem

Organizations move data but rarely verify it. Bad data (missing fields,
duplicates, invalid values, wrong types) silently corrupts dashboards, models,
and decisions. Sentinel validates data *before* it is trusted.

## 2. Semester 1 objective

Accept a dataset, validate every row against a declarative data contract, store
valid and invalid rows separately, explain each failure, and report dataset
health — all over a documented REST API.

## 3. In scope

- CSV upload endpoint
- Data contracts stored as configuration (`validation_rules` table)
- Validation rule engine supporting 6 rule types:
  `not_null`, `positive`, `in_set`, `valid_date`, `unique`, `regex`
- Valid rows stored in `valid_records`; failed rows in `quarantine` with reasons
- Health report endpoint (totals, health score, most common error)
- REST API with OpenAPI docs at `/docs`
- Dockerized dev environment (`docker compose up`)
- pytest suite covering the rule engine
- GitHub Actions CI running tests on every PR
- Minimal dashboard/page showing results
- Public free-tier deployment (Render + Neon) for the demo

## 4. Explicitly OUT of scope (deferred)

Streaming ingestion, scheduled pipelines, retries, freshness jobs, AI telemetry,
PII redaction, audit logs, authentication, cloud orchestration, lineage, high
availability. These belong to Semesters 2–3 and must not be started until the
Semester 1 deliverable is submitted.

## 5. Data model

Four tables: `datasets`, `validation_rules`, `valid_records`, `quarantine`.
Rows are stored as JSONB so any dataset shape validates without per-dataset
schema migrations.

## 6. API surface

```
GET    /health
POST   /datasets/upload
POST   /datasets/{id}/validate
GET    /datasets
GET    /datasets/{id}/report
GET    /datasets/{id}/quarantine
POST   /rules
GET    /rules?dataset=orders
DELETE /rules/{id}
```

## 7. Definition of Done

- `docker compose up` → `localhost:8000/docs` live and interactive
- Upload real CSV → define contract → validate → correct health report
- Good/bad rows routed correctly; every bad row has a readable reason
- 6 rule types, each covered by pytest
- Faker-corrupted fixture proves expected valid/invalid counts
- No secret ever committed to git
- CI green on every PR
- Deployed to a public URL for faculty demo

## 8. Team

Two engineers. Shared foundation setup, then split by seam (validation engine
vs API layer), with cross-review on every pull request.
