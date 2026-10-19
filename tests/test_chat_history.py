import ast
import json
import sqlite3
import uuid
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "app.py"


@pytest.fixture
def chat_api(tmp_path):
    source = APP_PATH.read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    wanted = {
        "get_auth_connection", "list_chats",
        "save_chat", "create_chat", "delete_chat",
    }
    functions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    assert {node.name for node in functions} == wanted

    db_path = tmp_path / "isolated_chat_test.db"
    namespace = {
        "sqlite3": sqlite3,
        "json": json,
        "uuid": uuid,
        "AUTH_DB": db_path,
    }
    module = ast.Module(body=functions, type_ignores=[])
    exec(compile(module, str(APP_PATH), "exec"), namespace)

    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE chat_conversations (
                chat_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL DEFAULT 'New chat',
                messages_json TEXT NOT NULL DEFAULT '[]',
                is_pinned INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

    return namespace


def test_multiple_chats_persist_independently(chat_api):
    create = chat_api["create_chat"]
    save = chat_api["save_chat"]
    listing = chat_api["list_chats"]

    first_id, _ = create(0, "First chat")
    original = [
        {"role": "assistant", "content": "Welcome"},
        {"role": "user", "content": "Keep this message"},
        {"role": "assistant", "content": "Original answer"},
    ]
    save(0, first_id, "First chat", original)

    second_id, second_messages = create(0, "New chat")

    chats = {item["chat_id"]: item for item in listing(0)}
    assert first_id != second_id
    assert first_id in chats and second_id in chats
    assert chats[first_id]["messages"] == original
    assert chats[second_id]["messages"] == second_messages


def test_chat_save_is_scoped_to_owner(chat_api):
    create = chat_api["create_chat"]
    save = chat_api["save_chat"]
    listing = chat_api["list_chats"]

    chat_id, _ = create(7, "Owner chat")
    save(8, chat_id, "Attempted overwrite", [
        {"role": "user", "content": "Unauthorized change"}
    ])

    owner_chat = listing(7)[0]
    assert owner_chat["title"] == "Owner chat"
    assert all(item["chat_id"] != chat_id for item in listing(8))


def test_delete_removes_only_selected_users_chat(chat_api):
    create = chat_api["create_chat"]
    delete = chat_api["delete_chat"]
    listing = chat_api["list_chats"]

    first_id, _ = create(0, "Keep")
    second_id, _ = create(0, "Delete")
    other_user_id, _ = create(9, "Other owner")

    delete(0, second_id)

    remaining = {item["chat_id"] for item in listing(0)}
    assert first_id in remaining
    assert second_id not in remaining
    assert other_user_id in {
        item["chat_id"] for item in listing(9)
    }


def test_clear_handler_creates_new_chat_without_overwriting_old():
    source = APP_PATH.read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    handlers = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not isinstance(test, ast.Call) or not isinstance(test.func, ast.Attribute):
            continue
        if test.func.attr != "button" or not test.args:
            continue
        label = test.args[0]
        if isinstance(label, ast.Constant) and label.value == "Clear current conversation":
            handlers.append(node)

    assert len(handlers) == 1
    calls = [
        n.func.id for n in ast.walk(handlers[0])
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    ]
    assert "create_chat" in calls
    assert "save_chat" not in calls
