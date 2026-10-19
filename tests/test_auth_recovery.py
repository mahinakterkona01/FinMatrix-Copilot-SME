import ast
import hashlib
import hmac
import secrets
import sqlite3
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "app.py").read_text(encoding="utf-8-sig")
TREE = ast.parse(SOURCE)
NAMES = {
    "get_auth_connection", "password_digest", "_identity_key",
    "login_is_limited", "record_login_failure",
    "reset_password_with_recovery",
}

@pytest.fixture
def api(tmp_path):
    found = [
        node for node in TREE.body
        if isinstance(node, ast.FunctionDef) and node.name in NAMES
    ]
    assert {node.name for node in found} == NAMES

    db_path = tmp_path / "isolated_auth_test.db"
    namespace = {
        "sqlite3": sqlite3, "hashlib": hashlib, "hmac": hmac,
        "secrets": secrets, "time": time, "AUTH_DB": db_path,
    }
    exec(compile(ast.Module(body=found, type_ignores=[]), str(ROOT / "app.py"), "exec"), namespace)

    with sqlite3.connect(db_path) as conn:
        conn.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                recovery_hash TEXT,
                recovery_salt TEXT
            );
            CREATE TABLE auth_rate_limits (
                identity_key TEXT PRIMARY KEY,
                failed_attempts INTEGER NOT NULL DEFAULT 0,
                window_started REAL NOT NULL,
                locked_until REAL NOT NULL DEFAULT 0
            );
        """)
        salt = "11" * 16
        code = "RECOVERY-TEST-9472"
        digest = namespace["password_digest"](code, salt)
        conn.execute(
            """INSERT INTO users
               (username,email,full_name,password_hash,password_salt,recovery_hash,recovery_salt)
               VALUES(?,?,?,?,?,?,?)""",
            ("testuser", "test@example.com", "Test User", "old-hash", "22" * 16, digest, salt),
        )
    namespace["test_code"] = code
    return namespace

def test_wrong_recovery_code_is_counted(api):
    ok, message = api["reset_password_with_recovery"](
        "testuser", "wrong-code", "NewSecurePassword123"
    )
    assert not ok
    assert "Recovery failed" in message
    limited, _ = api["login_is_limited"]("testuser")
    assert not limited

def test_five_failed_recovery_attempts_trigger_lockout(api):
    reset = api["reset_password_with_recovery"]
    for _ in range(5):
        ok, _ = reset("testuser", "wrong-code", "NewSecurePassword123")
        assert not ok
    limited, _ = api["login_is_limited"]("testuser")
    assert limited
    ok, message = reset("testuser", api["test_code"], "NewSecurePassword123")
    assert not ok
    assert "Too many recovery attempts" in message

def test_successful_recovery_consumes_code_and_clears_limit(api):
    reset = api["reset_password_with_recovery"]
    ok, message = reset("testuser", api["test_code"], "NewSecurePassword123")
    assert ok
    assert "consumed" in message.lower()

    ok_again, message_again = reset(
        "testuser", api["test_code"], "AnotherSecurePassword456"
    )
    assert not ok_again
    assert "Recovery failed" in message_again

def test_unknown_account_failure_is_generic(api):
    ok, message = api["reset_password_with_recovery"](
        "unknown-user", "wrong-code", "NewSecurePassword123"
    )
    assert not ok
    assert message == "Recovery failed. Check the account details and recovery code."
