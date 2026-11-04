# -*- coding: utf-8 -*-
"""
routes/home.py
==============
首页 + 个人中心 + 设置接口。设置接口仅登录用户可访问，游客无法修改 AI 配置。
"""
from flask import Blueprint, jsonify, render_template, request

from config import settings as cfg
from db import get_user_by_id
from utils.auth import current_user_id, is_logged_in, login_required

bp = Blueprint("home", __name__)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/advisor")
def advisor_page():
    return render_template("advisor.html")


@bp.get("/compare")
def compare_page():
    return render_template("compare.html")


@bp.get("/troubleshoot")
def troubleshoot_page():
    return render_template("troubleshoot.html")


@bp.get("/profile")
def profile():
    """个人中心：登录用户显示账号信息，游客显示“游客模式”。"""
    user = None
    if is_logged_in():
        user = get_user_by_id(current_user_id())
    return render_template("profile.html", user=user)


@bp.get("/api/settings")
@login_required
def get_settings_api():
    s = dict(cfg.get_settings())
    s["has_api_key"] = bool(s.get("api_key"))
    s["api_key"] = "******" if s["api_key"] else ""   # 不回显完整密钥
    s["data_dir"] = cfg.DATA_DIR
    return jsonify({"ok": True, "settings": s})


@bp.post("/api/settings")
@login_required
def save_settings_api():
    data = request.get_json(silent=True) or {}
    api_key = (data.get("api_key") or "").strip()
    base_url = (data.get("base_url") or "").strip()
    model = (data.get("model") or "").strip()
    if api_key in ("", "******"):
        api_key = cfg.get_settings().get("api_key", "")
    new = {
        "api_key": api_key,
        "base_url": base_url if base_url else cfg.get_settings().get("base_url", "https://api.openai.com/v1"),
        "model": model,
        "temperature": data.get("temperature", 0.7),
    }
    cfg.save_settings(new)
    return jsonify({"ok": True, "message": "设置已保存到 D 盘 data/settings.json"})
