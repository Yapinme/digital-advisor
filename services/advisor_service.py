# -*- coding: utf-8 -*-
"""
services/advisor_service.py
===========================
模块1：新机选购 AI 逻辑。
核心规则：
- 严格遵守预算区间，禁止推荐超出预算 100 元以上商品；
- 按品类、用途推荐；
- 价格精确到百位；
- 预算内找不到合适品牌时，说明品牌最低预算并给平替。
未配置 API Key 时自动降级为本地演示数据（同样遵守上述规则）。
"""
import json
import re

from config import settings as cfg
from services import ai_client


def _load_prompt() -> dict:
    """读取 D 盘 prompts.json 中选购模块的提示词。"""
    with open("%s/config/prompts.json" % cfg.PROJECT_ROOT, "r", encoding="utf-8-sig") as f:
        return json.load(f)["advisor"]


def _parse_budget(budget: str):
    """
    解析前端拼接的预算文本：
      "2000元~4500元" / "2000元以上" / "5000元以内"
    返回 (min_price, max_price)，0 表示不限制。
    """
    budget = budget or ""
    nums = [int(n) for n in re.findall(r"\d+", budget.replace(",", ""))]
    min_price, max_price = 0, 0
    if "以上" in budget and nums:
        min_price = nums[0]
    elif "以内" in budget and nums:
        max_price = nums[0]
    elif "~" in budget or "至" in budget:
        if len(nums) >= 2:
            min_price, max_price = nums[0], nums[1]
    elif nums:
        max_price = nums[0]
    return min_price, max_price


def _round_100(price: int) -> int:
    """价格精确到百位。"""
    return int(round(price / 100.0) * 100)


def _rough_price(price: int) -> str:
    """用于提示文案的裸价格，如 1300 元。"""
    return f"{_round_100(price)} 元"


def _fmt_price(price: int) -> str:
    """参考价精确到百位，输出如 参考价 1300 元。"""
    if not price:
        return "【暂无准确数据，仅供参考】"
    return f"参考价 {_round_100(price)} 元"


# 内置离线演示数据（示例价已按百位给出，仅供演示）
_OFFLINE_CATALOG = {
    "手机": [
        {"name": "红米 Note 系列（示例）", "brand": "小米", "price": 1299, "core_highlights": "续航约 10 小时、屏幕 6.6 英寸更大、日常够用", "disadvantages": "影像一般，夜景较弱", "target_users": "预算有限、办公/轻度娱乐"},
        {"name": "荣耀 X 系列（示例）", "brand": "荣耀", "price": 1999, "core_highlights": "性能均衡、快充够用", "disadvantages": "散热一般，重度游戏发热", "target_users": "学生党、日常拍照"},
        {"name": "华为 nova 系列（示例）", "brand": "华为", "price": 2499, "core_highlights": "影像调优好、轻薄", "disadvantages": "预算内存储版本较低", "target_users": "喜欢拍人像、自拍的用户"},
        {"name": "小米数字系列（示例）", "brand": "小米", "price": 3299, "core_highlights": "屏幕好、性能强、影像均衡", "disadvantages": "重量略大", "target_users": "拍照兼顾游戏的中高端用户"},
        {"name": "iPhone 入门款（示例）", "brand": "苹果", "price": 3999, "core_highlights": "系统流畅、视频稳定、生态好", "disadvantages": "存储偏小、充电较慢", "target_users": "iOS 生态或视频录制用户"},
    ],
    "耳机": [
        {"name": "入门级 TWS 耳机（示例）", "brand": "小米", "price": 199, "core_highlights": "便宜轻便、日常听歌够用", "disadvantages": "延迟与音质一般", "target_users": "通勤日常听歌"},
        {"name": "游戏低延时 TWS（示例）", "brand": "OPPO", "price": 399, "core_highlights": "低延迟、适合手游", "disadvantages": "需确认手机蓝牙协议支持", "target_users": "对延迟敏感的游戏玩家"},
        {"name": "头戴式游戏耳机（示例）", "brand": "漫步者", "price": 599, "core_highlights": "声场大、佩戴稳、延迟低", "disadvantages": "较占包、夏天较热", "target_users": "PC 端游戏玩家"},
    ],
    "笔记本": [
        {"name": "轻薄本（示例）", "brand": "联想", "price": 4599, "core_highlights": "便携、续航约 12 小时、办公稳定", "disadvantages": "性能一般，不适合重度游戏", "target_users": "办公、上课、轻度创作"},
        {"name": "全能本（示例）", "brand": "华为", "price": 6599, "core_highlights": "性能与便携平衡、屏幕好", "disadvantages": "机身偏厚", "target_users": "兼顾办公与轻度游戏"},
        {"name": "游戏本（示例）", "brand": "戴尔", "price": 7499, "core_highlights": "独显性能强、适合游戏", "disadvantages": "重且续航短", "target_users": "重游戏/3D 渲染"},
    ],
    "平板": [
        {"name": "影音平板（示例）", "brand": "联想", "price": 1799, "core_highlights": "屏幕大、追剧上网课舒适", "disadvantages": "性能中规中矩", "target_users": "追剧、上网课"},
        {"name": "创作平板（示例）", "brand": "华为", "price": 3299, "core_highlights": "手写笔体验好、性能强", "disadvantages": "配件价格高", "target_users": "绘画、办公、记笔记"},
    ],
    "相机": [
        {"name": "CCD 卡片机（平替，示例）", "brand": "通用", "price": 899, "core_highlights": "便宜轻便、复古氛围直出", "disadvantages": "画质与画幅有限、高感差", "target_users": "预算有限、喜欢复古直出的新手"},
        {"name": "微单入门款（示例）", "brand": "索尼", "price": 5299, "core_highlights": "画质好、轻便、可换镜头", "disadvantages": "镜头需另购", "target_users": "新手入门摄影"},
        {"name": "全画幅微单（示例）", "brand": "索尼", "price": 12999, "core_highlights": "高感强、画质顶级", "disadvantages": "贵、重", "target_users": "专业摄影"},
    ],
}


def _offline_advisor(category: str, budget: str, brands: list, usage: str) -> dict:
    """离线演示：严格按预算过滤 + 平替兜底。"""
    min_price, max_price = _parse_budget(budget)
    brands = brands or []
    items = list(_OFFLINE_CATALOG.get(category, _OFFLINE_CATALOG["手机"]))

    # 按预算过滤（价格需在区间内，禁止超出）
    in_budget = [
        it for it in items
        if (not max_price or it["price"] <= max_price)
        and (not min_price or it["price"] >= min_price)
    ] if (min_price or max_price) else list(items)

    if not in_budget:
        # 整个品类预算内都没有商品：说明最低起步价
        cheapest = min(items, key=lambda x: x["price"])
        brand_info = ""
        if brands:
            bmin = min((it["price"] for it in items if it["brand"] in brands), default=None)
            if bmin is not None:
                brand_info = f"所选品牌最低约 {_rough_price(bmin)}；"
                if bmin > (max_price or 0):
                    brand_info += "已超出当前预算。"
        note = f"{brand_info}你选择的「{category}」在当前预算内暂无合适商品，该品类最低约起步价 {_rough_price(cheapest['price'])}（{cheapest['name']}）。预算到位后再考虑。"
        # 尽力找预算内的平替（可能来自更便宜替代品）
        return {
            "title": f"{category} 在预算 {budget} 内暂无合适商品",
            "notice": note,
            "recommendations": [],
            "summary": f"{note} 若坚持当前预算，建议先考虑二手或降低配置需求。",
        }

    # 品牌偏好优先
    if brands:
        matched = [it for it in in_budget if it["brand"] in brands]
        if matched:
            rec_items = matched
            notice = ""
        else:
            # 预算内没有所选品牌：说明该品牌最低起步预算，再用预算内其它品牌平替
            brand_min = min((it["price"] for it in items if it["brand"] in brands), default=None)
            if brand_min is not None:
                brand_note = f"所选品牌（{'、'.join(brands)}）最低起步约 {_rough_price(brand_min)}，超出当前预算；"
            else:
                brand_note = "所选品牌暂无可示例产品，"
            alternative = in_budget[0]
            notice = f"{brand_note}预算内以下为同品类平替推荐："
            rec_items = [alternative]
    else:
        rec_items = in_budget
        notice = ""

    rec_items = sorted(rec_items, key=lambda x: x["price"])[:3]
    recommendations = [{
        "name": it["name"],
        "price": _fmt_price(it["price"]),
        "core_highlights": it["core_highlights"],
        "disadvantages": it["disadvantages"],
        "target_users": it["target_users"],
    } for it in rec_items]

    summary = f"（离线演示模式：未配置大模型，以下为内置示例数据，仅供演示；配置 API Key 后输出更准确）预算 {budget}，品类 {category}，用途偏 {usage}，参考以上推荐。"
    if notice:
        summary += "\n" + notice
    return {
        "title": f"{category} · 预算 {budget} 的推荐结果",
        "notice": notice,
        "recommendations": recommendations,
        "summary": summary,
    }


def generate_advisor_reply(category: str, budget: str, brands=None, usage: str = "", notes: str = "") -> dict:
    """返回 {"title":.., "notice":.., "recommendations":[...], "summary":...}"""
    brands = brands or []
    brands_text = "、".join(brands) if brands else "不限"

    if not ai_client.is_configured():
        return _offline_advisor(category, budget, brands, usage)

    p = _load_prompt()
    user_msg = p["user_template"].format(
        budget=budget,
        category=category,
        brands=brands_text,
        usage=usage,
        notes=notes or "无",
    )
    messages = [
        {"role": "system", "content": p["system_prompt"]},
        {"role": "user", "content": user_msg},
    ]
    raw = ai_client.chat(messages, temperature=0.7, json_object=True)
    try:
        start = raw.find("{")
        end = raw.rfind("}")
        result = json.loads(raw[start:end + 1])
        result.setdefault("notice", "")
        result.setdefault("recommendations", [])
        return result
    except Exception:
        return {"title": "AI 返回格式异常", "notice": "", "recommendations": [], "summary": raw[:500]}
