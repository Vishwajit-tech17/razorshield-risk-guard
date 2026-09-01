# ============================================================
# RAZORSHIELD AI - DAY 10
# AUDIT DATABASE
# ============================================================

import sqlite3
from datetime import datetime
from pathlib import Path


# Database will be created inside backend/
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "razorshield_audit.db"


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """
    connection = sqlite3.connect(DATABASE_PATH)

    # Allows rows to behave like dictionaries
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Create the audit table if it does not already exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS review_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            transaction_id TEXT NOT NULL,

            amount REAL,
            risk_probability REAL,
            risk_percentage REAL,
            risk_level TEXT,

            ai_recommendation TEXT,
            ai_reasoning TEXT,
            policy_evidence TEXT,

            human_decision TEXT,
            reviewer_note TEXT,

            timestamp TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def save_review(
    transaction_id,
    amount,
    risk_probability,
    risk_percentage,
    risk_level,
    ai_recommendation,
    ai_reasoning,
    policy_evidence,
    human_decision,
    reviewer_note
):
    """
    Save one completed human-review decision.
    """

    # Safe string conversion for complex types (lists, dicts) before SQLite binding
    if isinstance(ai_reasoning, list):
        ai_reasoning = "\n".join(str(item) for item in ai_reasoning)
    elif not isinstance(ai_reasoning, str):
        ai_reasoning = str(ai_reasoning) if ai_reasoning is not None else ""

    if isinstance(policy_evidence, list):
        formatted_policies = []
        for item in policy_evidence:
            if isinstance(item, dict):
                p_text = item.get("policy", str(item))
                score = item.get("score")
                formatted_policies.append(f"{p_text} (Relevance: {score})" if score is not None else p_text)
            else:
                formatted_policies.append(str(item))
        policy_evidence = "\n\n".join(formatted_policies)
    elif not isinstance(policy_evidence, str):
        policy_evidence = str(policy_evidence) if policy_evidence is not None else ""

    timestamp = datetime.now().isoformat(timespec="seconds")

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO review_audit (
            transaction_id,
            amount,
            risk_probability,
            risk_percentage,
            risk_level,
            ai_recommendation,
            ai_reasoning,
            policy_evidence,
            human_decision,
            reviewer_note,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            transaction_id,
            amount,
            risk_probability,
            risk_percentage,
            risk_level,
            ai_recommendation,
            ai_reasoning,
            policy_evidence,
            human_decision,
            reviewer_note,
            timestamp
        )
    )

    connection.commit()

    audit_id = cursor.lastrowid

    connection.close()

    return {
        "id": audit_id,
        "transaction_id": transaction_id,
        "human_decision": human_decision,
        "reviewer_note": reviewer_note,
        "timestamp": timestamp
    }


def get_all_reviews():
    """
    Return all audit records, newest first.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM review_audit
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]