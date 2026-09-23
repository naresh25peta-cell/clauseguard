"""
schema.py — defines and creates the SQLite tables.

SQLite keeps this runnable locally without any cloud credentials; a hosted
version would swap this for a managed SQL database.

Tables:
  - NominationRules  : reference rules; CN extractions are compared against these
  - CNExtractions    : one row per field per PDF run (audit trail + scoring)
  - MSARiskResults   : clause-by-clause risk ratings from MSA scans

NominationRules has 9 extraction fields + 4 identity columns.
"""
import sqlite3
from pathlib import Path
from clauseguard.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # NominationRules — mirrors RulesDB. AgreementGuid + TradeGroupId identify the rule.
    # One TradeGroupId can have 0–N rules (median 1, max ~10 per PROFILE.md analysis).
    cur.execute("""
        CREATE TABLE IF NOT EXISTS NominationRules (
            id                       INTEGER PRIMARY KEY AUTOINCREMENT,
            -- Identity columns (from RulesDB join)
            AgreementGuid            TEXT NOT NULL,
            AgreementName            TEXT,
            TradeGroupId             TEXT NOT NULL,
            TradeName                TEXT,
            NominationRuleId         TEXT,
            -- Extraction target columns (7 fields from prompts)
            NominationRuleDescription TEXT,
            AgreementSection         TEXT,   -- Vessel|LoadLocation|Quantity|DischargeLocation|ArrivalWindow|blank
            OptionOwner              TEXT,   -- seller|counterparty|mutual
            AnchorType               TEXT,   -- WindowStart|InitialWindow|Commented|SalesWindow|SpecificDate|Unknown
            Complexity               TEXT,   -- DateExpression|SimpleAnchor
            AnchorDirection          TEXT,   -- Before|After
            NominationRuleTitle      TEXT,
            -- Derived fields (post-processing, out of scope for skeleton)
            DateExpression           TEXT,
            TargetDate               TEXT
        )
    """)

    # CNExtractions — one row per field per run, with LLM score vs NominationRules.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS CNExtractions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            FileName         TEXT NOT NULL,
            AgreementGuid    TEXT,
            TradeGroupId     TEXT,
            FieldName        TEXT NOT NULL,
            ExtractedValue   TEXT,
            ExpectedValue    TEXT,
            LLMScore         INTEGER,   -- 1 (poor) to 5 (exact match)
            ScoreReasoning   TEXT,
            RunAt            TEXT DEFAULT (datetime('now'))
        )
    """)

    # MSARiskResults — one row per clause per MSA scan.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS MSARiskResults (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            FileName    TEXT NOT NULL,
            ClauseRef   TEXT,
            ClauseText  TEXT,
            RiskRating  TEXT,   -- Red|Amber|Green
            Reasoning   TEXT,
            UseCase     TEXT,   -- periodic|cmo_check|draft_validation
            RunAt       TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()
    print("Database tables created.")
