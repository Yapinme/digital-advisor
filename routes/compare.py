# -*- coding: utf-8 -*-
"""
routes/compare.py
=================
模块2：参数对比。负责输入校验、调用对比服务、保存/读取/删除对比记录。
"""
import json

from flask import Blueprint, jsonify, request

from db import (clear_compare_records, delete_compare_record, get_compare_record,
                list_compare_records, save_compare_record)
from services import compare_service
from utils import validation

bp = Blueprint("compare", __name__)


@bp.post("/api/compare")
def run_compare():
    data = request.get_json(silent=True) or {}
    ok, a = validation.validate_text("产品 A", data.get("a"), required=True, max_len=100)
    if not ok:
        return jsonify({"ok": False, "error": a}), 400
    ok, b = validation.validate_text("产品 B", data.get("b"), required=True, max_len=100)
    if not ok:
        return jsonify({"ok": False, "error": b}), 400
    ok, notes = validation.validate_text("关注点", data.get("notes"), required=False, max_len=500)
    if not ok:
        return jsonify({"ok": False, "error": notes}), 400

    result = compare_service.generate_compare_reply(a, b, notes)
    return jsonify({"ok": True, "result": result})


@bp.post("/api/compare/save")
def save_compare():
    """前端把已生成的结果保存到 SQLite。"""
    data = request.get_json(silent=True) or {}
    ok, a = validation.validate_text("产品 A", data.get("a"), required=True, max_len=100)
    if not ok:
        return jsonify({"ok": False, "error": a}), 400
    ok, b = validation.validate_text("产品 B", data.get("b"), required=True, max_len=100)
    if not ok:
        return jsonify({"ok": False, "error": b}), 400
    result = data.get("result") or ""
    rid = save_compare_record({"a": a, "b": b}, json.dumps(result, ensure_ascii=False))
    return jsonify({"ok": True, "id": rid})


@bp.get("/api/compare/records")
def compare_records():
    return jsonify({"ok": True, "records": list_compare_records()})


@bp.get("/api/compare/records/<int:rid>")
def compare_record_detail(rid):
    row = get_compare_record(rid)
    if not row:
        return jsonify({"ok": False, "error": "记录不存在"}), 404
    return jsonify({"ok": True, "record": row})


@bp.delete("/api/compare/records/clear")
def compare_records_clear():
    count = clear_compare_records()
    return jsonify({"ok": True, "deleted": count})


@bp.delete("/api/compare/records/<int:rid>")
def compare_record_delete(rid):
    delete_compare_record(rid)
    return jsonify({"ok": True})
