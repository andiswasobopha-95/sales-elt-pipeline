# Sales Analytics ELT Pipeline

A production-style ELT pipeline that extracts product catalog data from a public
REST API, generates realistic synthetic order/transaction data on top of it,
loads everything into PostgreSQL, transforms it into an analytics-ready star
schema with **dbt**, and is orchestrated end-to-end with **Apache Airflow** —
all running locally via **Docker Compose**.

Built as a portfolio project to demonstrate core data engineering skills:
pipeline design, orchestration, data modeling, testing, and CI/CD.

## Architecture

```
                ┌──────────────────┐
                │  Fake Store API  │   (public REST API - product catalog)
                └────────┬─────────┘
                         │  extract (Python + requests)
                         ▼
                ┌──────────────────┐
                │  data/raw/*.json │   raw landing zone
                └────────┬─────────┘
                         │  synthesize orders + load (Python + psycopg2)
                         ▼
                ┌──────────────────┐
                │   PostgreSQL     │   raw schema (products, orders, order_items)
                └────────┬─────────┘
                         │  transform (dbt)
                         ▼
        ┌────────────────┴────────────────┐
        │   staging models (stg_*)        │  cleaned, typed, renamed
        └────────────────┬────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │   mart models (dim_*, fct_*)     │  star schema for analytics
        └──────────────────────────────────┘
                         │
                         ▼
                 BI tool / notebook

  Orchestrated end-to-end by an Airflow DAG (extract → load → dbt run → dbt test)
```

## Stack

| Layer          | Tool                              |
|----------------|------------------------------------|
| Extraction     | Python, `requests`                 |
| Storage        | PostgreSQL 15                      |
| Transformation | dbt-core + dbt-postgres            |
| Orchestration  | Apache Airflow 2.x (LocalExecutor) |
| Containers     | Docker & Docker Compose            |
| Testing        | pytest, dbt tests                  |
| CI             | GitHub Actions                     |

## Why this project

Real APIs rarely hand you transactional data for free, so this project pulls
**real** product data from [Fake Store API](https://fakestoreapi.com) and
layers **synthetic but realistic** orders on top (seeded random generation,
so results are reproducible). This mirrors a common real-world pattern:
combining a reference/master data source with transactional data from another
system — while keeping the project runnable by anyone, with no API keys.

## Project layout

```
sales-elt-pipeline/
├── dags/                      # Airflow DAG definitions
│   └── sales_pipeline_dag.py
├── src/
│   ├── extract/                # Pull data from the API
│   │   └── extract_api.py
│   ├── load/                   # Load raw + synthetic data into Postgres
│   │   └── load_to_postgres.py
│   └── utils/                  # Shared helpers (db connection, logging)
│       ├── db.py
│       └── logger.py
├── dbt_project/                 # dbt models (staging + marts) and tests
│   ├── models/staging/
│   ├── models/marts/
│   └── dbt_project.yml
├── sql/
│   └── create_tables.sql        # Raw schema DDL
├── tests/                       # pytest unit tests for extract/load code
├── data/                        # Local raw JSON landing zone (gitignored)
├── docker-compose.yml           # Postgres + Airflow, one command to run all
├── requirements.txt
├── Makefile                     # Convenience commands
└── .github/workflows/ci.yml     # Lint + unit tests + dbt compile on push
```

## Getting started

### Prerequisites
- Docker & Docker Compose
- Make (optional, but the Makefile makes this much easier)

### 1. Clone and configure
```bash
cp .env.example .env
```

### 2. Spin up the stack
```bash
make up
```
This starts Postgres and Airflow (webserver + scheduler). Airflow UI is at
`http://localhost:8080` (user: `admin`, pass: `admin`).

### 3. Run the pipeline manually (without Airflow, for quick testing)
```bash
make etl        # extract -> load -> dbt run -> dbt test
```

### 4. Or trigger it from Airflow
Unpause the `sales_elt_pipeline` DAG in the UI, or:
```bash
docker compose exec airflow-webserver airflow dags trigger sales_elt_pipeline
```

### 5. Run tests
```bash
make test        # pytest unit tests
make dbt-test     # dbt data quality tests
```

## Data model

**Staging layer** (`stg_products`, `stg_orders`, `stg_order_items`): 1:1 cleaned
views over raw tables — renamed columns, cast types, no business logic.

**Marts layer** (star schema):
- `dim_products` — product dimension (category, price, rating)
- `dim_dates` — date dimension for time-based analysis
- `fct_orders` — order fact table
- `fct_order_items` — line-item grain fact table, the primary analytics table

Example downstream question this schema answers: *"What's monthly revenue by
product category, and how does it trend?"*

## What I'd extend next
- Swap synthetic orders for a second real API/CDC source
- Add a data quality framework (Great Expectations) alongside dbt tests
- Deploy Airflow + Postgres to a cloud environment (ECS/Cloud Composer)
- Add incremental dbt models instead of full-refresh
- Add a lightweight BI layer (Metabase) via docker-compose

## License
MIT — free to use as a template for your own portfolio.
