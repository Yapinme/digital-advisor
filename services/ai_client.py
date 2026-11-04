# -*- coding: utf-8 -*-
"""
services/ai_client.py
=====================
大模型文本 API 统一调用层（OpenAI 兼容协议）。
配置从 D 盘 data/settings.json 读取，未配置时抛 AINotConfigured。
"""
import json
import urllib.request
import urllib.error

from config import settings as cfg


class AINotConfigured(Exception):
    """未配置 API Key 时的异常。"""


class AICallError(Exception):
    """调用大模型失败。"""


def is_configured() -> bool:
    s = cfg.get_settings()
    return bool((s.get("api_key") or "").strip())


def _resolve_url(base_url: str) -> str:
    base = (base_url or "https://api.openai.com/v1").strip().rstrip("/")
    if base.endswith("/chat/completions"):
        base = base.rsplit("/chat/completions", 1)[0].rstrip("/")
    return base + "/chat/completions"


def chat(messages, temperature=0.7, json_object=False, max_tokens=1600):
    """调用大模型获取补全文本。

    messages: [{"role":"system|user|assistant","content":"..."}]
    返回: AI 输出的文本字符串。
    """
    s = cfg.get_settings()
    api_key = (s.get("api_key") or "").strip()
    if not api_key:
        raise AINotConfigured("尚未配置大模型 API Key，请在页面右上角“设置”中填写。")

    model = (s.get("model") or "").strip() or "gpt-4o-mini"
    temperature = float(s.get("temperature") or 0.7)

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_object:
        payload["response_format"] = {"type": "json_object"}

    req = urllib.request.Request(
        _resolve_url(s.get("base_url") or ""),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8")[:500]
        except Exception:
            pass
        raise AICallError(f"大模型接口返回错误（HTTP {e.code}）：{detail}")
    except urllib.error.URLError as e:
        raise AICallError(f"无法连接大模型接口：{e.reason}")

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise AICallError("大模型返回内容格式异常。")

    return content
