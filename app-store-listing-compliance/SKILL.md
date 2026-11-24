---
name: app-store-listing-compliance
description: "用公开证据逐条判 iOS App 是否违反 Apple App Review Guidelines 与上架页要求（分级、订阅披露、隐私标签、DSA 交易者、第三方 AI 共享）。Use when asked 查 App Store 合规风险 / 会不会被拒审 / 订阅披露够不够 / 隐私标签与政策是否一致."
version: 1.0.0
author: shiftu
platforms: [macos, linux]
prerequisites:
  commands: [python3, hermes]
---

# app-store-listing-compliance — App Store 上架合规判定

对**已上架**的 iOS App 逐条判定 Apple App Review Guidelines 与上架页要求（含 DPLA Schedule 2 披露、EU DSA 交易者信息、年龄分级、5.1.2(i) 第三方 AI 数据共享）。

**判的是公开可见证据，不是审核结果。** 没有源码、没有 App Store Connect 权限；需要安装包或后台才能确认的条款一律 `无法从外部判断` 并写清「需要什么」。

规则库 43 条（`rules/apple_rules.json`，`verified_on` 见文件头），覆盖台账 `rules/coverage_ledger.md`，官方原文快照 `rules/sources/apple/`。

## 触发场景

- 「这款 iOS App 在 App Store 有什么合规风险 / 会不会被拒」
- 「订阅披露够不够 / 隐私政策与隐私标签对不对得上」
- 「新 App 上架前预检」「被拒了帮我定位是哪条」
- 批量自查里的 iOS 部分

## 一条命令跑完

```bash
scripts/run_app.sh <trackId 或 apps.apple.com URL> <out_dir> [app 名称] [judge]
```

例：`scripts/run_app.sh 1234567890 runs ExampleApp`

第 4 参数写 `judge` 表示跳过取数、只用已有 `_raw/` 重跑判定。

流水线（每步都能单独跑）：

| 步骤 | 命令 | 产物 |
|---|---|---|
| 1 取数 | `scripts/fetch_listing.py <id> <out_dir> [--countries us,de]` | `_raw/*`（HTML + 可见文本）、`listing.json`、`script_verdicts.json`、`_logs/fetch_<date>.jsonl` |
| 2 判定 | `run_app.sh` 内置：拼 prompt → `hermes chat --query-file` → 合并 `script_verdicts.json` | `_raw/prompt.md`、`_raw/llm_output.txt`、`verdicts.json` |
| 3 闸门 | `scripts/check_run.py <out_dir> <slug>` | 退出码（0 = 全过） |
| 4 报告 | `scripts/render_report.py <out_dir> <slug>` | `report.md`（五段） |

<out_dir>/<slug>/ 下依次生成：`_raw/` → `listing.json` → `script_verdicts.json` → `verdicts.json` → `report.md`。

## 硬性规则（违反即失败）

1. **只写查到的。** 每条判定挂证据：`find`（`_raw` 快照里的**逐字子串**）或 `absent`（机械确认的缺失 + 为什么该缺失算证据）。凭印象判定一律作废。
2. **`不符合` 必须有正面证据。** 只靠「页面上没看到」不能判违规——降级 `无法从外部判断` 并写清缺什么。真实案例：某 App 页面上「App Support」行缺失，但页脚含 Support 字样，无法排除渲染丢行。
3. **`不适用` ≠ `符合`。** 条款前提不成立（无该功能 / 分类不符 / 分级已覆盖）写 `不适用`，并给证据说明前提为何不成立；不得记成 `符合`，否则「符合」的数字失去意义。
4. **先过闸门再汇报。** `check_run.py` 输出 `RESULT: ok` 才算完成；FAIL 就修到过。闸门会重算 summary、逐条比对 `find` 是否逐字命中。
5. **页面 404 ≠ 抓取失败。** 产品页 404 写 `status=delisted`（下架是结论），不重试当故障处理。
6. **绝不预测结果。** 只给「哪条不符合 + 证据 + 条款后果 + 怎么改」，不写「会通过」「会被拒」。
7. **未生效条款不算违规。** `status=upcoming` 只进 `deadlines[]`，不进计数、不进风险等级。
8. **规则库超 60 天要声明。** `verified_on` 距抓取日 > 60 天时，报告首段后会自动插 `⚠️ 规则库可能过期`；此时先跑 `scripts/refresh_sources.sh` 复核，再采信结论。

## 取数拿到什么

Apple 侧 6–8 个请求，全部落 `_raw/`（原响应 + 去 script/style 的可见文本）：

- `itunes.apple.com/lookup?id=<id>&country=<us|de>` — 结构化字段（名称/卖家/版本/价格/描述/截图数）
- `apps.apple.com/<cc>/app/id<id>` — 产品页：分级行、Contains 行、In-App Purchases 区、App Privacy 段、隐私政策/EULA 链接；DE 页另含 EU 交易者块（`Anbieter` / `DUNS`）
- 产品页上的隐私政策页、EULA、App Support（抓不到记 `missing[]`，不猜 URL）

每个请求写一行 `_logs/fetch_<date>.jsonl`（`ts/tool/query_or_url/status/used_for`）。**没有日志行的 URL 不得出现在 `sources[]`。**
只依赖 Python 标准库（`urllib`/`html.parser`），不需要 bs4。

`listing.json` 的字段按来源分层：`app`（汇总）、`fields[*].source`（每个字段来自哪个文件）、`evidence_files[]`（证据白名单）。契约见 `references/schema.md`。

## 怎么判（route 四档）

| route | 条数 | 怎么判 |
|---|---|---|
| `script` | 15 条已由 `fetch_listing.py` 直接定论 | 分级取值、标题字符数、隐私/EULA 链接 HTTP 状态、EU 交易者块有无、IAP 申报、DSA/policy 引用、Kids 分类、真钱博彩与医疗声明、强制评分措辞、占位文本、其他平台名 |
| `llm` | 读政策/条款做语义比对 | 5.1.2(i) 第三方 AI 是否具名、5.1.1(v) 删号、5.1.2(ii) 用途、4.8 登录替代、4.7 托管责任、隐私标签 vs 政策 |
| `vision` | 3 条 | 2.3.8 元数据 4+ 观感、2.3.14 创意素材、2.3.3 截图须展示真实界面——没图片一律 `无法从外部判断` |
| `human_only` | 3 条 | 2.5.19 隐藏功能、4.3(a) 多 Bundle ID、4.3(b) 竞品对比 |

判之前先看每条规则的 `observability` / `surface` / `route` / `verify` / `false_positive_notes`。
一条义务横跨「公开页可查」与「只能后台核实」时，用 `layers[]` 逐层给结论，**不要因为深层判不了就把整条降级成无法判断**。

**按店面判，不要只看 US**：分级、DSA 交易者块、站外购买链接都有店面差异，至少抓 US + 一个 EU 店面。

## 报告

五段固定顺序（`render_report.py` 生成，不要手写）：

1. 结论 — 四项计数 + 不符合按 severity 分布
2. 阻断项（removal 级）— 每条带 rule_id、条号、条款原句、逐字证据、后果、修法
3. 疑似违规（rejection / advisory）
4. 即将到期（upcoming，只列不判）
5. 无法核实（`无法从外部判断` + `不适用` 清单）

风险等级按**违规规则的 severity**，不按条数：有 removal 不符合 → 🔴；只有 rejection/advisory → 🟡；无不符合但未知 > 40% → ⚪；否则 🟢。
模板与写作规则见 `references/report_template.md`，判定口径与防误报见 `references/judging.md`。

## 覆盖台账

`rules/coverage_ledger.md` 列出指南全部条号 + 非条号必查项（分级问卷 / DSA 交易者 / DPLA 附则 2）的去向：对应规则 id、可做但未建规则（vision）、或「仅人工 + 理由」。问到「某个条号为什么没判」先查台账再回答。

## 维护规则库

```bash
scripts/validate_rules.py rules/apple_rules.json   # 结构 / 枚举 / 引文 / 日志命中
scripts/verify_quotes.py                           # 每条 quote 必须逐字出现在 rules/sources/ 快照里
scripts/refresh_sources.sh                         # 重抓官方页，核对 quote 是否仍存在（--keep 另存新正文）
```

`refresh_sources.sh` 用「quote 是否仍逐字存在」判变化，不比较版面（快照是 bs4 按 selector 抓的，整页重抓必然格式不同）。有 quote 失配 → 退出码 1，更新 `quote` 与 `verified_on` 后再跑 `verify_quotes.py`。

## 已踩过的坑

- **引文口径是「原始文本逐字」**，不是「去掉 markdown 后能对上」。跨 `[链接](url)` 或 `**加粗**` 的句子要截到标记之外；撇号用原文的 `’` 或 `'`。
- **`contentAdvisoryRating`（Lookup）是旧字段**：API 返回 `17+`、产品页显示 `18+`（新体系）。以页面为准。
- **「App 隐私」区块里的 `Diagnostics` 不是医疗声明**——声明类条款只看 `_raw/<slug>_description.txt`。
- **DSA 交易者信息只在 EU 国家页出现**，US 页没有是正常的，别误判。
- **AI 供应商未具名**是 5.1.2(i) 下最高频的实质问题：广告 SDK 逐一具名，模型供应商却写「trusted technology providers」。判 `不符合` 时在 note 写明「是否另有单独同意弹窗需二进制复核」。
- **价格货币混用**（`99 रुपये $0.99` 与 `Weekly $2.99` 并列）说明部分内购只在印度区配了本地价：标 🟡，不算硬违规。
- **截图类规则不可判**：2.3.3 / 2.3.8 / 2.3.14 都要看图，没接图像判定前一律 `无法从外部判断`，不要用描述文本代替。
- **4.3(b) 有两句**：饱和品类不接受无差异新提交；以及存量「未更新/未改进」可被移除。老应用不能当已过关。
- **分级问卷 2026-11-16 起多两个描述项**（Dating and Relationships → 至少 18+；Shared Location → 巴西 A16），上架早于该日的 App 未必答过，报告里单列。

## 文件

```
SKILL.md
rules/apple_rules.json          43 条规则（route/status/severity/verify/fix/quote/source_url）
rules/coverage_ledger.{json,md} 条号覆盖台账
rules/sources/apple/*.md        官方原文快照（refresh_sources.sh 用它判变化）
rules/sources/POLICY_CHANGES.md 政策变更记录
references/schema.md            listing.json / verdicts.json 契约
references/judging.md           判定口径与防误报
references/report_template.md   五段报告模板
references/prompt_template.md   判定 prompt 的契约
scripts/fetch_listing.py        取数（stdlib）
scripts/run_app.sh              一条命令跑完
scripts/check_run.py            闸门（任一不过即非零退出）
scripts/render_report.py        五段报告
scripts/validate_rules.py       规则库结构校验
scripts/verify_quotes.py        引文逐字闸门
scripts/refresh_sources.sh      官方页复核
_logs/fetch_<date>.jsonl        规则库自身的抓取留痕
```
