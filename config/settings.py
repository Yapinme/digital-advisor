# -*- coding: utf-8 -*-
"""
config/settings.py
==================
全局配置：所有缓存、临时文件、数据库、日志都放在 D 盘项目目录下，
避免写入 C 盘导致系统盘膨胀。
"""
import os

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 各类数据目录：全部固定在 D 盘项目目录内
DATA_DIR   = os.path.join(PROJECT_ROOT, "data")
LOG_DIR    = os.path.join(PROJECT_ROOT, "logs")
CACHE_DIR  = os.path.join(PROJECT_ROOT, "cache")
TMP_DIR    = os.path.join(PROJECT_ROOT, "tmp")

SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

for _d in (DATA_DIR, LOG_DIR, CACHE_DIR, TMP_DIR):
    os.makedirs(_d, exist_ok=True)

# 让 Python 的 tempfile 也默认使用 D 盘临时目录
os.environ.setdefault("TMPDIR", TMP_DIR)
os.environ.setdefault("TEMP", TMP_DIR)
os.environ.setdefault("TMP", TMP_DIR)

DEFAULT_SETTINGS = {
    "api_key":  os.environ.get("OPENAI_API_KEY", ""),
    "base_url": os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    "model":    os.environ.get("OPENAI_MODEL", ""),
    "temperature": 0.7,
}


def _load_settings():
    import json
    if not os.path.exists(SETTINGS_FILE):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data or {})
        return merged
    except Exception:
        return dict(DEFAULT_SETTINGS)


def get_settings():
    return _load_settings()


def save_settings(new_settings):
    import json
    allowed = ("api_key", "base_url", "model", "temperature")
    cur = _load_settings()
    for k in allowed:
        if k in new_settings and new_settings[k] is not None:
            cur[k] = new_settings[k]
    try:
        cur["temperature"] = max(0.0, min(2.0, float(cur.get("temperature", 0.7))))
    except (TypeError, ValueError):
        cur["temperature"] = 0.7
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(cur, f, ensure_ascii=False, indent=2)
    return cur
