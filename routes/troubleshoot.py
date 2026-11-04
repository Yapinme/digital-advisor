# -*- coding: utf-8 -*-
"""
routes/troubleshoot.py
======================
模块3：故障问诊。对话式，前端把完整消息历史传回，后端返回下一步指导。
"""
from flask import Blueprint, jsonify, request

from services import troubleshoot_service
from utils import validation

bp = Blueprint("troubleshoot", __name__)


@bp.post("/api/troubleshoot")
def run_troubleshoot():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages") or []
    if not isinstance(messages, list) or len(messages) == 0:
        return jsonify({"ok": False, "error": "请先描述你的设备故障情况。"}), 400

    # 只取最近的 20 条，避免上下文过长
    messages = messages[-20:]
    # 过滤空消息
    cleaned = []
    for m in messages:
        content = validation.normalize(m.get("content"))
        if content:
            role = m.get("role") in ("user", "assistant") and m.get("role") or "user"
            if validation.seems_gibberish(content):
                return jsonify({"ok": False, "error": "检测到乱码输入，请用正常文字描述故障。"}), 400
            cleaned.append({"role": role, "content": content[:1200]})

    reply = troubleshoot_service.generate_troubleshoot_reply(cleaned)
    return jsonify({"ok": True, "reply": reply})
