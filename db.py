# -*- coding: utf-8 -*-
"""
db.py
=====
SQLite 数据库：表结构 + 记录读写。数据库文件固定放在 D 盘 data/ 下。
用户表 + 选购记录 + 对比记录。
"""
import hashlib
import json
import os
import secrets
import sqlite3

from config import settings as cfg

DB_PATH = os.path.join(cfg.DATA_DIR, "advisor.db")


def get_conn():
    os.makedirs(cfg.DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- 密码哈希（使用带随机盐的 PBKDF2）----------
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 120000)
    return salt + ":" + digest.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, saved = stored.split(":", 1)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 120000)
        return secrets.compare_digest(digest.hex(), saved)
    except Exception:
        return False


def init_db():
    """建表：用户表、选购记录、对比记录；首次运行创建默认管理员账号。"""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS advisor_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                request TEXT NOT NULL,
                result   TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS compare_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                request TEXT NOT NULL,
                result   TEXT NOT NULL
            )
        """)
    seed_default_user()


def seed_default_user():
    """首次运行时创建一个默认账号：admin / admin123（可在登录后自行注册更多账号）。"""
    with get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()
        if row and row["n"] == 0:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("admin", hash_password("admin123")),
            )


# ---------- 用户账户 ----------
def create_user(username: str, password: str):
    """创建用户；用户名已存在返回 False。"""
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hash_password(password)),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def find_user_by_username(username: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    return dict(row) if row else None


def get_user_by_id(uid: int):
    with get_conn() as conn:
        row = conn.execute("SELECT id, username, created_at FROM users WHERE id=?", (uid,)).fetchone()
    return dict(row) if row else None


def verify_login(username: str, password: str):
    """校验用户名密码，成功返回用户 dict，失败返回 None。"""
    user = find_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return {"id": user["id"], "username": user["username"]}


# ---------- 选购记录 ----------
def save_advisor_record(request: dict, result: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO advisor_records (request, result) VALUES (?, ?)",
            (json.dumps(request, ensure_ascii=False), result),
        )
        return cur.lastrowid


def list_advisor_records(limit=50):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, created_at, request, result FROM advisor_records ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_advisor_record(rid: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM advisor_records WHERE id=?", (rid,))
        return cur.rowcount > 0


def clear_advisor_records() -> int:
    """清空全部选购记录。"""
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM advisor_records")
        return cur.rowcount


# ---------- 对比记录 ----------
def save_compare_record(request: dict, result: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO compare_records (request, result) VALUES (?, ?)",
            (json.dumps(request, ensure_ascii=False), result),
        )
        return cur.lastrowid


def list_compare_records(limit=50):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, created_at, request, result FROM compare_records ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_compare_record(rid: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM compare_records WHERE id=?", (rid,)).fetchone()
    return dict(row) if row else None


def delete_compare_record(rid: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM compare_records WHERE id=?", (rid,))
        return cur.rowcount > 0


def clear_compare_records() -> int:
    """清空全部对比记录。"""
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM compare_records")
        return cur.rowcount
