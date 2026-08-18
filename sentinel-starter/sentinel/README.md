# Sentinel

Data reliability platform — validates datasets against data contracts, separates
good rows from bad, and explains every failure. Semester 1 = CSV validation +
quarantine pipeline over a REST API.

Stack: FastAPI · PostgreSQL · Docker Compose · pytest

---

## Run it 

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
├── core/         # config + db session  
├── models/       # SQLAlchemy tables     
└── tests/        # pytest                
```

## Security

`.env` is gitignored from commit #1. **Never commit real credentials or API
keys.** Config is loaded from environment variables via `app/core/config.py`.

#What each file does?

**app/schemas/contracts.py** — defines the agreed shapes: what a Rule looks like going in, and what a ValidationResult looks like coming out.
***app/services/engine.py*** — the engine: a registry of rules plus validate(), which runs every rule on every row and tallies the result.
***tests***-running tests update if any code broke,written using pytest.
