# Sentinel

Data reliability platform — validates datasets against data contracts, separates
good rows from bad, and explains every failure. Semester 1 = CSV validation +
quarantine pipeline over a REST API.

Stack: FastAPI · PostgreSQL · Docker Compose · pytest

---

## Run it (Day 1 definition of done)

```bash
# 1. Copy the env template and set a local password
cp .env.example .env      # then edit POSTGRES_PASSWORD + DATABASE_URL

# 2. Bring up API + database
docker compose up --build

# 3. Open the live API docs
#    http://localhost:8000/docs
#    http://localhost:8000/health  -> {"status":"ok","database":"connected"}
```

`docker compose up` starts Postgres, waits until it's healthy, then starts the
API with hot-reload. Tables are auto-created on startup for now (Alembic
migrations come in Semester 1 proper).

## Run the tests

```bash
docker compose exec app pytest -q
```

---

## Project layout

```
app/
├── api/          # (Sem 1) FastAPI routers — thin, no business logic
├── services/     # (Sem 1) validation engine + rule types — the brain
├── repositories/ # (Sem 1) all DB access
├── core/         # config + db session  ✅ done
├── models/       # SQLAlchemy tables     ✅ done
└── tests/        # pytest                ✅ started
```

## Security

`.env` is gitignored from commit #1. **Never commit real credentials or API
keys.** Config is loaded from environment variables via `app/core/config.py`.

## Role split

Pair on this Docker/skeleton setup together, then split:

- **Person A** — validation engine + rule types + tests (the brain) + data model
- **Person B** — API layer + CSV upload/ingestion + report endpoint + this README + dashboard

Swap PR reviewers every time, so both of you understand the whole system.
