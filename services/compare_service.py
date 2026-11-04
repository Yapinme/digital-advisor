# -*- coding: utf-8 -*-
"""
services/compare_service.py
===========================
模块2：数码产品参数对比 AI 逻辑。
固定输出 Markdown 表格 + 总结，并支持离线演示。
界面只展示纯文本：解析表格时会去掉 ** 等加粗标记。
"""
import json

from config import settings as cfg
from services import ai_client
from utils.markdown_parser import extract_markdown_table

_OFFLINE_TABLE = """| 对比项 | 产品A | 产品B |
| --- | --- | --- |
| 参考价格 | 示例产品 A【参考】 | 示例产品 B【参考】 |
| 处理器/芯片 | 【暂无准确数据，仅供参考】 | 【暂无准确数据，仅供参考】 |
| 屏幕 | 【暂无准确数据，仅供参考】 | 【暂无准确数据，仅供参考】 |
| 存储版本 | 【暂无准确数据，仅供参考】 | 【暂无准确数据，仅供参考】 |
| 主摄像头 | 【暂无准确数据，仅供参考】 | 【暂无准确数据，仅供参考】 |
| 电池与充电 | 【暂无准确数据，仅供参考】 | 【暂无准确数据，仅供参考】 |
| 特色功能 | 需根据具体型号核实 | 需根据具体型号核实 |
| 主要缺点 | 需根据具体型号核实 | 需根据具体型号核实 |

总结：当前为离线演示模式，未配置大模型 API，无法生成真实参数。请配置 API Key 后重新对比；下表为演示结构，具体数值请以官方资料为准。"""


def _load_prompt() -> dict:
    with open("%s/config/prompts.json" % cfg.PROJECT_ROOT, "r", encoding="utf-8-sig") as f:
        return json.load(f)["compare"]


def _plain(md: str) -> str:
    """把 Markdown 文本里的 ** 加粗标记去掉，只保留纯文本。"""
    return (md or "").replace("**", "")


def generate_compare_reply(product_name_a: str, product_name_b: str, notes: str) -> dict:
    """返回 {"markdown":.., "columns":.., "rows":.., "summary":..}"""
    if not ai_client.is_configured():
        md = _OFFLINE_TABLE.replace("产品A", product_name_a).replace("产品B", product_name_b)
        parsed = extract_markdown_table(md)
        return {"markdown": _plain(md), **parsed}

    p = _load_prompt()
    user_msg = p["user_template"].format(a=product_name_a, b=product_name_b, notes=notes or "无")
    messages = [
        {"role": "system", "content": p["system_prompt"]},
        {"role": "user", "content": user_msg},
    ]
    md = ai_client.chat(messages, temperature=0.5, json_object=False)
    parsed = extract_markdown_table(md)
    return {"markdown": _plain(md), **parsed}
