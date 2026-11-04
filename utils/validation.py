# -*- coding: utf-8 -*-
"""
utils/validation.py
===================
输入校验：过滤空输入、明显乱码 / 乱敲键盘 / 过长输入，并返回友好提示。
"""
import re

MAX_LEN = 1200  # 单个输入最大长度

_JUNK_SYMBOLS = set('@#$%^&*+=\\|/`~;:\'\"')


def is_blank(value) -> bool:
    """空输入 / 全空白 / None 判定。"""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
    return False


def normalize(value: str) -> str:
    return (value or "").strip()


def seems_gibberish(text: str) -> bool:
    """粗判是否为乱码/乱敲：控制字符多、重复字符过密、符号占比过高。"""
    if not text:
        return False
    # 控制字符
    if any(ord(c) < 32 and c not in "\r\n\t" for c in text):
        return True
    # 连续 10 个以上相同字符，通常是乱敲
    if re.search(r"(.)\1{9,}", text):
        return True
    # 无中文且无字母数字，只剩标点符号
    meaningful = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", text)
    if not meaningful:
        return True
    # 符号占比过高
    total = len(text) or 1
    symbol_ratio = sum(1 for c in text if c in _JUNK_SYMBOLS) / total
    if symbol_ratio > 0.4:
        return True
    return False


def validate_text(field_name: str, value, *, required=True, max_len=MAX_LEN):
    """
    校验并返回 (是否通过, 清洗后的值 或 错误信息)
    """
    text = normalize(value)
    if required and is_blank(text):
        return False, f"{field_name}不能为空，请重新输入。"
    if len(text) > max_len:
        return False, f"{field_name}内容过长（最多{max_len}字），请精简后重试。"
    if text and seems_gibberish(text):
        return False, f"{field_name}内容看起来像乱码，请重新输入正常描述。"
    return True, text
