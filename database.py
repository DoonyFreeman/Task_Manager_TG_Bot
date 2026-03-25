import sqlite3
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

DATABASE = "tasks.db"


@dataclass
class Task:
    id: int
    user_id: int
    text: str
    remind_at: datetime
    is_done: bool
    created_at: datetime


def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT,
            remind_at TEXT,
            is_done INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    conn.commit()
    return conn


def add_task(user_id: int, text: str, remind_at: datetime) -> int:
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, text, remind_at, created_at) VALUES (?, ?, ?, ?)",
        (user_id, text, remind_at.isoformat(), datetime.now().isoformat()),
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id


def get_tasks(user_id: int, include_done: bool = False) -> List[Task]:
    conn = init_db()
    cursor = conn.cursor()
    if include_done:
        cursor.execute(
            "SELECT id, user_id, text, remind_at, is_done, created_at FROM tasks WHERE user_id = ? ORDER BY remind_at",
            (user_id,),
        )
    else:
        cursor.execute(
            "SELECT id, user_id, text, remind_at, is_done, created_at FROM tasks WHERE user_id = ? AND is_done = 0 ORDER BY remind_at",
            (user_id,),
        )
    rows = cursor.fetchall()
    conn.close()
    return [
        Task(
            id=r[0],
            user_id=r[1],
            text=r[2],
            remind_at=datetime.fromisoformat(r[3]),
            is_done=bool(r[4]),
            created_at=datetime.fromisoformat(r[5]),
        )
        for r in rows
    ]


def mark_done(task_id: int) -> bool:
    conn = init_db()
    conn.execute("UPDATE tasks SET is_done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    changes = conn.total_changes > 0
    conn.close()
    return changes


def delete_task(task_id: int) -> bool:
    conn = init_db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    changes = conn.total_changes > 0
    conn.close()
    return changes


def get_task_by_id(task_id: int) -> Optional[Task]:
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, text, remind_at, is_done, created_at FROM tasks WHERE id = ?",
        (task_id,),
    )
    r = cursor.fetchone()
    conn.close()
    if r:
        return Task(
            id=r[0],
            user_id=r[1],
            text=r[2],
            remind_at=datetime.fromisoformat(r[3]),
            is_done=bool(r[4]),
            created_at=datetime.fromisoformat(r[5]),
        )
    return None
