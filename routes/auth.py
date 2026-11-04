# -*- coding: utf-8 -*-
"""
routes/auth.py
==============
登录 / 注册 / 退出 / 获取当前登录状态。
"""
from flask import Blueprint, jsonify, request

from db import create_user, get_user_by_id, verify_login
from utils import auth as auth_util
from utils import validation

bp = Blueprint("auth", __name__)


@bp.get("/api/auth/me")
def me():
    uid = auth_util.current_user_id()
    if not uid:
        return jsonify({"ok": True, "logged_in": False, "mode": "guest"})
    user = get_user_by_id(uid)
    if not user:
        auth_util.logout_user()
        return jsonify({"ok": True, "logged_in": False, "mode": "guest"})
    return jsonify({"ok": True, "logged_in": True, "mode": "user", "user": user})


@bp.post("/api/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    ok, username = validation.validate_text("账号", data.get("username"), required=True, max_len=30)
    if not ok:
        return jsonify({"ok": False, "error": username}), 400
    if not (data.get("username") or "").strip().isalnum():
        return jsonify({"ok": False, "error": "账号只能由字母或数字组成"}), 400
    ok, password = validation.validate_text("密码", data.get("password"), required=True, max_len=64)
    if not ok:
        return jsonify({"ok": False, "error": password}), 400
    if len(password) < 6:
        return jsonify({"ok": False, "error": "密码至少 6 位"}), 400
    if password != (data.get("confirm") or ""):
        return jsonify({"ok": False, "error": "两次输入的密码不一致"}), 400

    if create_user((data.get("username") or "").strip(), password):
        return jsonify({"ok": True, "message": "注册成功，请登录"})
    return jsonify({"ok": False, "error": "该账号已存在"}), 409


@bp.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"ok": False, "error": "请输入账号和密码"}), 400
    user = verify_login(username, password)
    if not user:
        return jsonify({"ok": False, "error": "账号或密码错误"}), 401
    auth_util.login_user(user["id"])
    return jsonify({"ok": True, "message": "登录成功", "user": user})


@bp.post("/api/auth/logout")
def logout():
    auth_util.logout_user()
    return jsonify({"ok": True, "message": "已退出登录"})
