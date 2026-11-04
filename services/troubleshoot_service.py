# -*- coding: utf-8 -*-
"""
services/troubleshoot_service.py
================================
模块3：数码设备故障 AI 问诊助手。
对话式：前端每轮把全部消息发来，服务端生成“下一步指导”。
"""
import json

from config import settings as cfg
from services import ai_client


def _load_prompt() -> dict:
    with open("%s/config/prompts.json" % cfg.PROJECT_ROOT, "r", encoding="utf-8-sig") as f:
        return json.load(f)["troubleshoot"]


def _offline_reply(user_text: str) -> str:
    """简单关键字离线版引导，仅用于未配置 API 时演示。"""
    t = user_text.lower()
    if any(k in t for k in ("wifi", "无线", "连不上网", "上不了网")):
        return "先试最简单的一步：\n① 关闭再打开设备的 Wi-Fi 开关；\n② 忘记当前网络后重新连接并输入密码。\n如果能连上说明是临时网络问题；还是不行，请在对话框回复“仍然不行”，我再帮你分步排查。"
    if any(k in t for k in ("耳机", "一边没声", "单边", "没声音")):
        return "先做最简单的一步：\n① 把耳机放进充电盒再取出，重新连接；\n② 用棉签轻擦耳机金属触点与手机孔（若有线）。\n若单边仍无声，请回复“仍然不行”，我接着判断是软件通道还是硬件故障。"
    if any(k in t for k in ("手机", "打不开", "不开机", "黑屏")):
        return "先试最简单的一步：\n长按电源键 10~15 秒强制重启，插上原装充电线充 10 分钟再开机。如果不能开机，回复“仍然不行”，我会引导你判断电池、屏幕还是主板问题。"
    return "先做最简单的一步：\n① 重启设备，看问题是否复现（电脑也建议再登录一次账号）；\n② 记录出现故障的时间点和具体报错信息，在下面回复给我。\n这样我能给出更准的下一步。"


def _plain(text: str) -> str:
    """去掉 Markdown 加粗（**）、斜体（*）和反引号，只保留纯文本。"""
    t = (text or "").replace("**", "").replace("__", "").replace("`", "")
    return t.strip()


def generate_troubleshoot_reply(messages: list) -> str:
    """messages 是前端传来的完整对话历史，每条 {role, content}。"""
    if not ai_client.is_configured():
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m.get("content", "")
                break
        return _offline_reply(last_user)

    p = _load_prompt()
    msgs = [{"role": "system", "content": p["system_prompt"]}]
    msgs += [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in messages]
    # 第一次用户消息时给一句引导词，让 AI 先追问一个关键问题
    if len([m for m in msgs if m["role"] == "user"]) == 1:
        msgs.append({"role": "system", "content": p["first_hint"]})
    return _plain(ai_client.chat(msgs, temperature=0.4, max_tokens=400))
