.PHONY: up down logs extract load etl test dbt-run dbt-test dbt-docs install

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f

install:
	pip install -r requirements.txt

extract:
	python -m src.extract.extract_api

load:
	python -m src.load.load_to_postgres

dbt-run:
	cd dbt_project && dbt run --profiles-dir .

dbt-test:
	cd dbt_project && dbt test --profiles-dir .

dbt-docs:
	cd dbt_project && dbt docs generate --profiles-dir . && dbt docs serve --profiles-dir .

etl: extract load dbt-run dbt-test

test:
	pytest tests/ -v
