# -*- coding: utf-8 -*-
"""
app.py
======
「数码选购 AI 顾问」Flask 入口文件。
启动：python app.py
默认监听本机 8000 端口，浏览器访问 http://127.0.0.1:8000
"""
import logging
import os
import secrets

from flask import Flask

from config import settings as cfg
from db import init_db
from routes import advisor, auth, compare, home, troubleshoot

# 日志固定写到 D 盘 logs/ 目录
LOG_FILE = os.path.join(cfg.LOG_DIR, "app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("digital-advisor")


def create_app():
    app = Flask(__name__)
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024   # 限制请求体 1MB，防异常大内容

    # 会话签名密钥：保存在 D 盘，避免每次重启都失效；若文件不存在则生成
    secret_file = os.path.join(cfg.DATA_DIR, "secret_key")
    if not os.path.exists(secret_file):
        with open(secret_file, "w", encoding="utf-8") as f:
            f.write(secrets.token_hex(32))
    with open(secret_file, "r", encoding="utf-8") as f:
        app.secret_key = f.read().strip()

    # 注册路由（登录 + 首页 + 选购 + 对比 + 问诊）
    app.register_blueprint(auth.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(advisor.bp)
    app.register_blueprint(compare.bp)
    app.register_blueprint(troubleshoot.bp)

    init_db()
    log.info("数据库已初始化：%s", cfg.DATA_DIR)
    return app


app = create_app()


if __name__ == "__main__":
    # host=127.0.0.1：只允许本机访问；课程演示如需局域网访问可改成 0.0.0.0
    app.run(host="127.0.0.1", port=8000, debug=False)
