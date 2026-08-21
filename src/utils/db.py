"""Shared PostgreSQL connection helper."""
import os

import psycopg2
from psycopg2.extensions import connection as PgConnection


def get_connection() -> PgConnection:
    """Create a psycopg2 connection using env vars (with sensible local defaults)."""
    host = os.environ.get("APP_DB_HOST", os.environ.get("POSTGRES_HOST", "localhost"))
    port = os.environ.get("APP_DB_PORT", os.environ.get("POSTGRES_PORT", "5433"))
    dbname = os.environ.get("APP_DB_NAME", os.environ.get("POSTGRES_DB", "sales_dw"))
    user = os.environ.get("APP_DB_USER", os.environ.get("POSTGRES_USER", "sales_user"))
    password = os.environ.get("APP_DB_PASSWORD", os.environ.get("POSTGRES_PASSWORD", "sales_pass"))

    return psycopg2.connect(
        host=host, port=port, dbname=dbname, user=user, password=password
    )
