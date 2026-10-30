# Sentinel

Data reliability platform. It validates datasets against declarative data
contracts, separates good rows from bad, and explains every failure.

**Semester 1** = CSV upload, rule-based validation, quarantine, health report,
REST API and a small dashboard.

**Live demo:** `https://<your-app>.onrender.com/ui/`  (API docs: `/docs`)

Stack: FastAPI · PostgreSQL · SQLAlchemy · Docker Compose · pytest · GitHub Actions

CI: tests run on every push and pull request.

---

## Run it locally

```bash
# 1. Copy the env template and set a local password
cp .env.example .env          # PowerShell: Copy-Item .env.example .env
# then edit POSTGRES_PASSWORD and the password inside DATABASE_URL

# 2. Start the API + database
docker compose up --build
```

- Dashboard: http://localhost:8000/ui/
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health -> `{"status":"ok","database":"connected"}`

`docker compose up` starts Postgres, waits until it is healthy, then starts the
API with hot-reload. Tables are created automatically on startup.

## Run the tests

```bash
docker compose exec app pytest -q
```

## How to demo

1. Open the dashboard (`/ui/`).
2. **Define the contract.** Keep the dataset name `orders` and add rules, for example:
   - `customer_id` / `not_null`
   - `amount` / `positive`
   - `status` / `in_set` with `{"allowed": ["pending", "paid", "shipped", "cancelled"]}`
3. **Upload a CSV.** Generate one with a known number of bad rows:
   ```bash
   docker compose exec app python -m app.scripts.generate_data
   ```
   This writes `app/scripts/sample.csv` with 200 rows, exactly 40 of them
   corrupted, so the expected result is 160 valid, 40 invalid, health 80%.
4. Click **Run validation**. The page shows the health score, valid/invalid
   counts, the most common error, and every quarantined row with its reason.

Shortcut: `docker compose exec app python -m app.scripts.seed_demo` loads a small
`demo_orders` dataset with its contract. Enter the id it prints under
"Use this id" and click **Run validation**.

---

## How it works

```
CSV upload ──> raw_records ──> orchestrator ──> engine ──┬─> valid_records
 (api/upload)   (landing zone)  (loads rules,    (applies  └─> quarantine
                                 runs engine,      rules)        (+ reasons)
                                 stores results)
                                       │
                                       └─> datasets (counts + health score)
```

1. **Ingestion:** `POST /datasets/upload` parses the CSV and stores each row as
   JSON in `raw_records`, untouched.
2. **Contract:** rules are rows in `validation_rules`, stored as data, not code.
3. **Validation:** `POST /datasets/{id}/validate` loads the dataset's rules and
   raw rows and runs them through the engine.
4. **Storage:** passing rows go to `valid_records`. Failing rows go to
   `quarantine` with the reason for every failed rule. Re-running is safe, since
   old results are cleared first.
5. **Reporting:** the dataset summary (totals, health score) is saved on
   `datasets`, and the report and quarantine endpoints read from it.

Health score = valid rows / total rows x 100.

### Rule types

| Rule | Passes when | Params |
|---|---|---|
| `not_null` | value is present and not empty | none |
| `positive` | value is a number greater than 0 | none |
| `in_set` | value is one of an allowed list | `{"allowed": [...]}` |
| `valid_date` | value parses as a date | `{"format": "%Y-%m-%d"}` (optional) |
| `unique` | value appears only once in its column | none |
| `regex` | value matches the pattern | `{"pattern": "..."}` |

`unique` is the one column-wide rule: it needs the whole column, so the engine
counts duplicates first and then checks each row. The other five look at one
row at a time.

### Data model

Five tables: `datasets`, `validation_rules`, `raw_records`, `valid_records`,
`quarantine`. Rows are stored as JSONB, so any CSV shape validates without
schema changes.

### API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness + database check |
| POST | `/datasets/upload?name=` | upload a CSV (multipart `file`) |
| GET | `/datasets` | list datasets |
| POST | `/datasets/{id}/validate` | run validation |
| GET | `/datasets/{id}/report` | totals, health score, most common error |
| GET | `/datasets/{id}/quarantine` | failed rows with reasons (`limit`, `offset`) |
| POST | `/rules` | add a rule to a contract |
| GET | `/rules?dataset=` | list a dataset's rules |
| DELETE | `/rules/{id}` | remove a rule |

---

## Project layout

```
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── static/index.html            # dashboard (plain HTML + JS)
└── app/
    ├── main.py                  # app setup, router registration
    ├── api/                     # thin FastAPI routers
    │   ├── upload.py            #   CSV ingestion
    │   ├── rules.py             #   contract CRUD
    │   ├── validation.py        #   validate, report, quarantine
    │   └── datasets.py          #   dataset list
    ├── services/
    │   ├── engine.py            #   the rules + validate()
    │   └── orchestrator.py      #   chains load -> validate -> store
    ├── schemas/contracts.py     # Rule in, ValidationResult out
    ├── models/tables.py         # SQLAlchemy tables
    ├── core/                    # config + db session
    ├── scripts/                 # seed_demo.py, generate_data.py
    └── tests/                   # pytest suite
```

## Deployment

The app runs on Render (Docker) with a Neon Postgres database. Set the
`DATABASE_URL` environment variable on Render to the Neon connection string,
written as `postgresql+psycopg2://...?sslmode=require`. Tables are created on
first boot.

## Security

`.env` is gitignored from commit #1. **Never commit real credentials or API
keys.** Config is read from environment variables via `app/core/config.py`.
