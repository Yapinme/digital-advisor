# -*- coding: utf-8 -*-
"""
utils/auth.py
=============
登录态辅助：基于 Flask 内置 session（签名 Cookie），
并提供 login_required 装饰器保护“仅登录用户”的接口。
"""
from functools import wraps

from flask import jsonify, session

SESSION_KEY = "uid"


def login_user(user_id: int):
    """把用户 id 写入 session，表示已登录。"""
    session[SESSION_KEY] = str(user_id)


def logout_user():
    session.pop(SESSION_KEY, None)


def current_user_id():
    v = session.get(SESSION_KEY)
    return int(v) if v else None


def is_logged_in() -> bool:
    return current_user_id() is not None


def login_required(fn):
    """装饰器：未登录时返回 401 JSON，前端可据此提示先登录。"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            return jsonify({"ok": False, "error": "请先登录后再操作（或使用游客模式使用 AI 助手）"}), 401
        return fn(*args, **kwargs)
    return wrapper
