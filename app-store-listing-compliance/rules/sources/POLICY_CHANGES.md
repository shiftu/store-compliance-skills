# 近期政策变化 —— 逐条官方核实

输入：`community/community_scan_reddit_forums.md` 第 4 节（二手线索）。
核实方式：只用 `_logs/fetch_2026-11-23.jsonl` 里有 `status=ok` 记录的官方页面；对每条给出官方原句或原始页面位置。核实日 2026-11-24。

状态口径：
- **已核实** = 官方页面能读到该表述（日期或条款文字至少一项）。
- **部分核实** = 条款文字核实，日期/区域清单来自二手。
- **未核实** = 官方页未读到（保留线索，不进规则库）。
- **超出范围** = 不是商店政策（州法 / 欧盟法），归 `geo-law-base`。

## Apple

| # | 线索 | 状态 | 官方依据 | 落到规则 |
|---|---|---|---|---|
| A1 | 5.1.2(i) 要求披露第三方（含第三方 AI）数据共享并取得明示同意 | 部分核实（条款在，2025-11 加入日期未见官方公告） | `sources/apple/guidelines.md` 5.1.2(i) 原文；规则 quote 已逐字校验 | `ASRG-5.1.2i-AI-SHARING` |
| A2 | 年龄分级改为 4+/9+/13+/16+/18+，新增问卷，2026-01-31 前完成 | **已核实** | `sources/apple/upcoming_requirements.md`：「Provide responses to the updated age rating questions for each of your apps by January 31, 2026」；新闻页 2025-07-24 | `ASRG-2.3.6-AGE-RATING`、`ASRG-AGE-RATING-FORM` |
| A3 | 2026-11-16 新增描述项 Dating and Relationships（至少 18+）与 Shared Location；2027-01-12 前完成；巴西 A18 / A16 | **已核实** | `sources/apple/news_index.md`（2026-11-02 公告）：「Starting November 16, 2026 … Dating and Relationships … Apps that include Dating and Relationships receive a minimum age rating of 18+ … must have these declarations completed by January 12, 2027 … In Brazil, local regulations require an A16 rating for Shared Location and an A18 rating for Dating and Relationships」 | 新增 `ASRG-AGE-DATING-COMPANION`、`ASRG-AGE-SHARED-LOCATION` |
| A4 | 2026-06-09 重写 4.3(b)：饱和品类、存量可移除 | 部分核实（条款文字与「We may remove…」均在 2026-10-16 版；2026-06-09 日期仅在二手来源） | `sources/apple/guidelines.md` 4.3(b) 原文 | `ASRG-4.3-FORTUNE`（改为 removal 句）、新增 `ASRG-4.3b-SATURATED` |
| A5 | 2026-10-16 修订：1.2 覆盖生成式 AI 与 AI 内容创作 App、非自愿私密影像；新增 2.5.19；新增 2.3.14；3.1.1(a) 重写 | **已核实** | `sources/apple/news_index.md`（October 16, 2026「Updated App Review Guidelines are now available」+「Strengthening … nonconsensual intimate imagery and bait-and-switch apps」）；`sources/apple/news_guidelines_2026-10-16.md` 有 3.1.1(a) 措辞变更 | `ASRG-1.2-PORN`、`ASRG-1.2-UGC`、`ASRG-2.5.19-HIDDEN`、`ASRG-2.3.14-ASSETS` |
| A6 | EU DSA：2025-02-17 起未申报交易者的 App 从 EU 店面移除 | **已核实** | `sources/apple/upcoming_requirements.md`：「Since February 17, 2025 … will be removed from the App Store in the European Union (EU) until trader status is provided and verified」 | `ASRG-DSA-TRADER` |
| A7 | 德州 SB2420 / 犹他 2027-05-06 / 路易斯安那 2027-07-01 年龄保证 | 超出范围 | 州法，非商店政策 | 不建规则；交 `geo-law-base`，报告第 4 段提示法域风险 |

## Google Play

| # | 线索 | 状态 | 官方依据 | 落到规则 |
|---|---|---|---|---|
| P1 | 2026-10-29 公告：Deceptive 涵盖操纵审核流程 | **已核实** | `sources/play/announcement_2026-10-29.md`；`sources/play/program_policies_2026-10-29.md`：「Attempts to manipulate Play review processes, including misleading reviewers … are strictly prohibited」 | `GP-DEC-02-REVIEW` |
| P1b | 同一公告：资格型折扣订阅须披露条件与后续价格（2027-01-27） | **已核实** | 公告原文 + `sources/play/subscriptions_eligibility.md` | `GP-SUB-05-ELIGIBILITY`（upcoming） |
| P1c | 同一公告：AI / agentic 体验的支付指引 | **已核实** | `sources/play/payments_guidance.md`（`#AI_agentic_experience`） | `GP-PAY-01-BILLING` |
| P1d | 同一公告：Play Age Signals 全球上线 | **已核实** | 公告原文 + `sources/play/age_signals.md` | 报告层（法域向），不建规则 |
| P1e | 同一公告：位置权限 2027-01-27 强制、Local Network / Manage Contacts 需声明（API 37+） | **已核实** | 公告原文 + `sources/play/sensitive_permissions.md` | `GP-SENS-01-LOCATION` |
| P2 | 全体开发者 2027-02-01 前申报交易者状态，否则资料与全部 App 全球移除 | **已核实** | `sources/play/trader_status.md`：「must be completed by February 1, 2027 … may trigger enforcement including app update blocks and removal from the Play Store globally」 | `GP-TRADER-01-DSA`（upcoming） |
| P3 | AI 政策页 URL 为 `answer/18265346` | **已核实**（性质不同） | 18265346 是**全量 Developer Program Policy（2026-10-29 生效版）**，AI-Generated Content 在 557 行；AI 专属页是 `answer/13985936`（本目录 `sources/play/ai_generated.md`）。两者不冲突，引用时要说明层级 | 已补抓 `sources/play/program_policies_2026-10-29.md` |
| P4 | AI 生成的商店素材需标注，网页商店显示「AI」标签 | **未核实**（仅 Reddit） | 官方 Policy / 帮助页未读到该要求 | 不建规则；第 4 段标「未审计信号」 |
| P5 | Android 开发者验证：2026-09-30 起巴西 / 印尼 / 新加坡 / 泰国；2027-01 全球 | **部分核实** | `sources/play/android_developer_verification.md`：「Effective September 30, 2026 … select regions … We'll continue rolling out user protections globally in 2027」；具体国家清单在 `/developer-verification/guides#locations`，未抓 | `GP-DEV-01-VERIFY`、`GP-PKG-01-REGISTER` |
| P6 | 健康类申报对所有 App 必填，非受监管健康 App 需免责声明 | **已核实** | `sources/play/health.md`：「Health and medical apps must complete the Health apps declaration form in Play Console」+「must include a clear disclaimer … not a medical device」 | `GP-HEALTH-02-DISCLAIMER` |
| P7 | EU AI Act 第 50 条 2026-08-02 适用 | 超出范围 | 欧盟法，非商店政策 | 不建规则；交 `geo-law-base` |

## 核实结论对目录的影响

1. Apple 规则 39 → **43**（新增 4.3b-SATURATED、2.3.10、2.3.3、AGE-SHARED-LOCATION），Play 仍 37；合计 80。
2. `ASRG-AGE-DATING-COMPANION` 从「二手截止日」升级为官方核实（2026-11-16 生效 / 2027-01-12 截止 / 巴西 A18）。
3. `ASRG-4.3-FORTUNE` 的 quote 换成官方「We may remove…」句，severity 保持 `removal`；原「饱和品类不接受新提交」拆成独立规则 `ASRG-4.3b-SATURATED`（rejection），两条各占一句原文，都 ≤300 字符。
4. 新增 `sources/play/program_policies_2026-10-29.md`（264,671 字符）作为全量政策主干，用于核对零散页面是否漏条款。
5. 未核实的两项（P4 AI 素材标签、A4 的 2026-06-09 日期）不进规则库，只在报告第 4 段作为「未审计信号」出现。
