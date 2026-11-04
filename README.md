# 数码选购 AI 顾问 项目说明

## 1. 项目简介
一、项目背景
现在数码产品更新换代非常快，手机、耳机、笔记本等品类型号繁多、参数复杂、价格区间跨度大。普通消费者在选购时常常面临三个问题：
1. 不知道自己的预算能买到什么，容易被营销话术和广告误导。
2. 想对比两款产品，但官方参数分散，逐个查官网很费时间。
3. 设备出故障（如连不上 Wi-Fi、耳机单边无声）时，不知道先查哪里，直接送修又可能被多收费。
本项目希望通过一个部署在本地的 Web 应用，用 AI 帮助用户完成新机选购、参数对比和故障排查，把复杂的数码消费决策变得直观、清晰、可操作。项目同时面向课程展示，强调代码简洁、结构清晰、易于讲解，并坚持把数据库、日志、缓存和临时文件全部放在 D 盘，避免占用 C 盘空间。
二、功能说明
项目包含三个核心模块：
1. 新机选购
用户填写预算区间（最低价 / 最高价）、选择产品品类和主要用途，还可以单选或多选品牌偏好。系统调用大模型生成推荐清单，每款产品包含产品名称、参考价格、核心亮点、缺点和适合人群。推荐严格遵守预算，不会超预算随意堆产品；如果预算内找不到合适品牌，会说明该品牌的最低预算，并做平替推荐。
同时支持保存选购记录，记录可以查看、删除，也可以一键清空，方便课堂上反复演示。
2. 参数对比
用户可输入两款数码产品型号（例如 iPhone 17 Pro 和华为 Mate 70），系统调用大模型生成结构统一的对比表格和一段纯文本总结，帮助用户快速针对性判断数码产品。对比结果支持一键复制，也可以保存为对比记录，随时查看、删除或清空。
3. 故障问诊
用户直接描述设备故障（如笔记本连不上 Wi-Fi、耳机一边没声音），系统以对话方式分步引导排查，先提供简单的解决方案，再逐步深入高级方案，并区分软件问题与硬件故障。新对话页面提供常见故障快捷按钮，例如手机充不进电、笔记本连不上 Wi-Fi、显示已保存但一直要密码、键盘按键失灵，用户点击即可快速提问。
三、项目亮点
1. AI 驱动，三位一体
   把「选购、对比、问诊」三个常见的数码决策场景统一到一个 Web 应用里，用大模型输出个性化建议，贴合真实使用需求。
2. 严格预算与平替方案
   新机选购会严格遵守用户预算，预算不足时主动提示品牌最低预算并推荐平替产品（例如预算不够买相机时推荐 CCD 卡片机），更贴近真实购物心理。
3. 输出简洁、不做虚假参数
   大模型参数不确定时明确标注「暂无准确数据，仅供参考」，禁止编造虚假参数；参数对比和故障问诊界面全部输出纯文本，不使用加粗等 Markdown 标记，界面风格干净整洁。
4. 模块化架构，适合课程讲解
   后端按选购、对比、问诊拆分路由和业务服务，前端使用原生 HTML/CSS/JavaScript，不引入复杂框架，代码带注释，适合大学生阅读和二次开发。
5. 提示词与业务代码分离
   三个模块的提示词统一放在 config/prompts.json，修改 AI 语气、输出格式、字段名时只需改 JSON，不需要改动业务代码。
6. 输入校验完善
   对空输入、明显乱码、超长输入都做了校验和友好提示，避免异常数据进入大模型或数据库。
7. 数据全部存放 D 盘
   所有 SQLite 数据库、日志、缓存、临时文件、API 配置都固定在 D 盘项目目录，密码管理、设置写入均在本机完成，不占用 C 盘，也便于清理和备份。
8. 支持离线演示模式
   未配置大模型 API 时，应用自动进入离线演示模式，三个模块都能完整走通流程，适合课堂先演示界面和交互，再接入真实 API。
9. 登录、游客模式与个人中心
   支持游客免登录直接使用，也支持账号注册和登录，登录后右上角显示当前用户名并进入个人中心，可修改大模型 API 配置。
10. 深色模式与动态交互
    网站右上角提供月亮图标切换深色模式，主题偏好保存在浏览器；首页提供三功能卡片入口，参数对比、故障问诊等页面均支持一键复制结果。

提示：未配置大模型 API 时，应用自动进入离线演示模式，可完整走通三个模块流程，适合课堂上先演示界面与逻辑；接入真实 API 后输出会更准确。

## 2. 技术栈
- 后端：Python 3 + Flask 3
- 前端：HTML + CSS + JavaScript（原生，无框架，易读）
- 存储：SQLite（Python 内置 sqlite3），数据库文件在 D 盘
- AI：OpenAI 兼容接口（/chat/completions），支持火山方舟 Agent Plan、DeepSeek、Kimi、通义、OpenAI 等兼容服务商
- 依赖：仅 Flask（其余全用 Python 标准库）

## 3. 存储位置（重要：全部放在 D 盘，不占用 C 盘）
| 类型 | 路径 |
|---|---|
| 项目根目录 | D:\codex\digital-advisor\ |
| SQLite 数据库 | D:\codex\digital-advisor\data\advisor.db |
| API 设置 | D:\codex\digital-advisor\data\settings.json |
| 运行日志 | D:\codex\digital-advisor\logs\app.log |
| 临时文件 | D:\codex\digital-advisor\tmp\ |
| 缓存 | D:\codex\digital-advisor\cache\ |
| 前端静态文件 | D:\codex\digital-advisor\static\ |
| 功能截图 | D:\codex\digital-advisor\screenshots\ |

源码中 config/settings.py 已把 TMP、TEMP、TMPDIR 环境变量指向 D 盘临时目录，确保 Python 临时文件也不写进 C 盘。

## 4. 目录结构
```
D:\codex\digital-advisor\
├── app.py                  # 入口：创建 Flask 应用、注册路由、初始化数据库
├── requirements.txt        # Python 依赖（flask）
├── start.bat               # Windows 一键启动脚本
├── start.ps1               # PowerShell 启动脚本
├── config/
│   ├── __init__.py
│   ├── settings.py         # 全局路径配置（全部指向 D 盘）+ 设置读写
│   └── prompts.json        # 三个模块的提示词（集中管理，方便修改提示词，不改业务代码）
├── routes/
│   ├── __init__.py
│   ├── home.py             # 首页 + 设置接口
│   ├── advisor.py          # 模块1 选购路由
│   ├── compare.py          # 模块2 对比路由
│   └── troubleshoot.py     # 模块3 问诊路由
├── services/
│   ├── __init__.py
│   ├── ai_client.py        # 大模型统一调用层（OpenAI 兼容）
│   ├── advisor_service.py  # 选购业务（含离线演示数据）
│   ├── compare_service.py  # 对比业务（固定 Markdown 表格解析）
│   └── troubleshoot_service.py  # 问诊业务（输出纯文本）
├── utils/
│   ├── __init__.py
│   ├── validation.py       # 输入校验（空输入、乱码、超长）
│   └── markdown_parser.py  # Markdown 表格解析（表格/总结分离，去加粗标记）
├── db.py                   # SQLite 建表与记录读写（含清空记录）
├── templates/              # Flask 模板（HTML 页面）
├── static/css/style.css    # 样式（含深色模式）
├── static/js/common.js     # 公共脚本（请求、复制、登录、设置、深色模式）
├── static/js/advisor.js    # 模块1 前端
├── static/js/compare.js    # 模块2 前端
├── static/js/troubleshoot.js  # 模块3 前端（常见故障快捷按钮）
├── data/                   # SQLite + settings（运行时自动生成）
├── logs/                   # 运行日志（运行时自动生成）
├── cache/ tmp/             # 缓存与临时目录（预留）
├── screenshots/            # 课程演示截图存放位置
└── README.md / DEMO_SCRIPT.md
```

## 5. 部署步骤（Windows 本机）
1. 确认已安装 Python 3.9 以上（本项目用 3.13 验证）。
2. 安装 Flask（只需一次）：
   ```bat
   python -m pip install -r D:\codex\digital-advisor\requirements.txt
   ```
3. 启动应用，任选其一：
   ```bat
   cd /d D:\codex\digital-advisor
   python app.py
   ```
   或双击 start.bat。
4. 浏览器打开：http://127.0.0.1:8000
5. 停止：在启动窗口按 Ctrl+C。

说明：默认只监听 127.0.0.1 本机访问，安全；如需局域网演示，把 app.py 最后一行 app.run(host="127.0.0.1", ...) 中 host 改为 0.0.0.0。

## 5.1 账号登录与游客模式
- 游客模式：打开应用即可直接使用新机选购、参数对比、故障问诊三个模块，无需登录。
- 登录：点击右上角登录按钮，输入账号密码。默认管理员账号：
  - 账号：admin
  - 密码：admin123
- 注册：在登录弹窗点注册账号可创建新账号（账号只能字母/数字，密码至少 6 位）。
- 登录后右上角显示当前用户名，可进入个人中心，并出现设置按钮，可修改大模型 API 配置。
- 用户、选购记录、对比记录都保存在 D:\codex\digital-advisor\data\advisor.db。

## 6. API 配置说明
1. 登录后打开网页右上角设置。
2. 填写：
   - API Key：服务商给你的密钥，例如 sk-xxxx 或火山方舟的 ark-xxxx。
   - Base URL：OpenAI 兼容接口地址。默认 https://api.openai.com/v1；火山方舟 Agent Plan 企业版填写 https://ark.cn-beijing.volces.com/api/plan/v3；DeepSeek 用 https://api.deepseek.com/v1，Kimi 用 https://api.moonshot.cn/v1 等。
   - 模型名称：服务商对应模型名，例如 gpt-4o-mini、deepseek-chat、ark-code-latest 等。
   - 温度：0 到 2 之间，数值越低输出越稳定。
3. 保存后，配置写入 D:\codex\digital-advisor\data\settings.json（密钥以明文存放在 D 盘本机，请勿外传）。
4. 也可以用 .env 或系统环境变量：OPENAI_API_KEY、OPENAI_BASE_URL、OPENAI_MODEL。
5. 密钥不会在网页上回显完整值，只会显示已配置。

提示词统一放在 config/prompts.json，想调整 AI 语气、输出格式、字段名，直接改这个 JSON 文件，无需改动路由与前端代码。

## 7. 功能截图位置
在 D:\codex\digital-advisor\screenshots\ 目录下存放演示截图。建议至少截 4 张：
- 01-home.png：首页功能卡片与新品宣传区
- 02-advisor.png：新机选购结果
- 03-compare.png：参数对比表格
- 04-troubleshoot.png：故障问诊对话
如果做视频，同时可参考 DEMO_SCRIPT.md。

## 8. 不足与优化方向
| 不足 | 优化方向 |
|---|---|
| 未配置 API Key 时为内置示例数据，非真实参数 | 接入大模型 API 后自动输出更准确；可进一步完善内置数据 |
| 大模型实时数据有限 | 后续可接入知乎开放平台搜索/CLI，获取真实行情与评测 |
| SQLite 用于演示足够，高并发一般 | 如需多人访问可换 PostgreSQL 或加缓存 |
| 仅本机部署 | 可加登录鉴权 + Docker 一键部署 |
| 参数对比依赖大模型输出 | 后续可建立自建参数库或官方数据源，做离线兜底 |
| 无后台管理页 | 可增加历史记录分页、导出 CSV/PDF |

## 9. 常见问题
- 为什么不能写入 D 盘？确认 D 盘存在且当前用户对该目录有写权限；项目刚创建时 data、logs 会自动生成。
- 连不上大模型接口？检查网络是否可访问对应服务商，Base URL 是否为 OpenAI 兼容格式，API Key 是否有效。
- 中文乱码？Windows 下用 python app.py 启动，日志中文可能受控制台编码影响，不影响网页与数据库；可用 chcp 65001 后再启动。
- 页面还是旧样式/旧功能？请在浏览器按 Ctrl+F5 强制刷新，清除缓存后再试。
