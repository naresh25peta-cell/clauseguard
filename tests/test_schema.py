"""
test_schema.py — tests that the database tables are created correctly
and that the seed data loads without errors.
"""
import os
import tempfile
import pytest
import sqlite3


@pytest.fixture
def tmp_db(monkeypatch):
    """Give each test its own throwaway SQLite file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    monkeypatch.setenv("DB_PATH", db_path)
    # Force config module to re-read the env var
    import importlib
    import clauseguard.config as cfg
    importlib.reload(cfg)
    import clauseguard.database.schema as schema
    importlib.reload(schema)
    yield db_path
    os.unlink(db_path)


def test_create_tables(tmp_db):
    from clauseguard.database.schema import create_tables, get_connection
    create_tables()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    conn.close()
    assert "NominationRules" in tables
    assert "CNExtractions" in tables
    assert "MSARiskResults" in tables


def test_seed_inserts_rows(tmp_db):
    from clauseguard.database.schema import create_tables, get_connection
    from clauseguard.database.seed import seed
    create_tables()
    seed()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM NominationRules")
    count = cur.fetchone()[0]
    conn.close()
    assert count == 3
