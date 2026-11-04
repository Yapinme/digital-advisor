# -*- coding: utf-8 -*-
"""
routes/advisor.py
=================
模块1：新机选购。负责校验输入、调用选购服务、保存/读取选购记录。
"""
import json

from flask import Blueprint, jsonify, request

from db import clear_advisor_records, delete_advisor_record, list_advisor_records, save_advisor_record
from services import advisor_service
from utils import validation

bp = Blueprint("advisor", __name__)


@bp.post("/api/advisor")
def run_advisor():
    data = request.get_json(silent=True) or {}

    ok, budget = validation.validate_text("预算", data.get("budget"), required=True, max_len=80)
    if not ok:
        return jsonify({"ok": False, "error": budget}), 400
    ok, category = validation.validate_text("品类", data.get("category"), required=True, max_len=50)
    if not ok:
        return jsonify({"ok": False, "error": category}), 400
    ok, usage = validation.validate_text("用途", data.get("usage"), required=True, max_len=50)
    if not ok:
        return jsonify({"ok": False, "error": usage}), 400
    ok, notes = validation.validate_text("额外说明", data.get("notes"), required=False, max_len=500)
    if not ok:
        return jsonify({"ok": False, "error": notes}), 400

    # 品牌：可选的多选列表
    brands_raw = data.get("brands")
    brands = []
    if isinstance(brands_raw, list):
        for b in brands_raw[:20]:
            txt = validation.normalize(b)
            if txt and not validation.seems_gibberish(txt) and len(txt) <= 30 and txt not in brands:
                brands.append(txt)
    brand_text = "、".join(brands) if brands else "不限"

    result = advisor_service.generate_advisor_reply(category, budget, brands, usage, notes)
    save_advisor_record(
        {"budget": budget, "category": category, "usage": usage, "brands": brands, "notes": notes},
        json.dumps(result, ensure_ascii=False),
    )
    return jsonify({"ok": True, "result": result})


@bp.get("/api/advisor/records")
def advisor_records():
    return jsonify({"ok": True, "records": list_advisor_records()})


@bp.delete("/api/advisor/records/clear")
def advisor_records_clear():
    count = clear_advisor_records()
    return jsonify({"ok": True, "deleted": count})


@bp.delete("/api/advisor/records/<int:rid>")
def advisor_record_delete(rid):
    delete_advisor_record(rid)
    return jsonify({"ok": True})
