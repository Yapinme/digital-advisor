# -*- coding: utf-8 -*-
"""
utils/markdown_parser.py
========================
把大模型返回的 Markdown 文本切分成「表格」和「总结」两部分，
方便前端把表格渲染为 HTML 表格。所有解析结果一律去掉 ** 加粗标记，
保证页面只输出纯文本。
"""
import re


def _plain(text: str) -> str:
    """去掉常见的 Markdown 强调符号（**、__、`、* 单星）只保留纯文本。"""
    t = (text or "").replace("**", "").replace("__", "").replace("`", "")
    # 去掉单个 * 包裹的斜体（谨慎：不影响普通星号较多场景）
    t = re.sub(r"\*([^*]+)\*", r"\1", t)
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", t)  # 图片
    return t.strip()


def extract_markdown_table(markdown_text: str):
    """
    从 markdown 文本中解析第一张表格。
    返回: {
        "columns": ["对比项", "产品A", "产品B"],
        "rows": [ ["参考价格", "xxx", "yyy"], ... ],
        "summary": "表格之后的总结文本"
    }
    """
    lines = (markdown_text or "").splitlines()
    table_lines = []
    summary_start = None
    i = 0
    # 找出第一段表格
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("|"):
            table_lines.append(line)
        else:
            if table_lines:
                summary_start = i
                break
        i += 1

    columns, rows = [], []
    parsed = []
    for raw in table_lines:
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        if all(re.fullmatch(r":*-+:*", c) for c in cells):
            continue  # 分隔行
        parsed.append(cells)

    if parsed:
        columns = [_plain(c) for c in parsed[0]]
        rows = [[_plain(c) for c in row] for row in parsed[1:]]

    # 总结部分 = 表格结束之后剩余内容
    summary = ""
    if summary_start is not None:
        rest = lines[summary_start:]
        # 去掉可能的标题与空行
        summary = "\n".join(x for x in rest if x.strip()).strip()
        summary = _plain(summary)

    return {"columns": columns, "rows": rows, "summary": summary}