# store-compliance-skills

两个 [Hermes Agent](https://github.com/NousResearch/hermes-agent) skill：只凭**公开可见的证据**，逐条判定一款已上架 App 是否违反商店政策。不需要源码，也不需要 App Store Connect / Play Console 权限。

| Skill | 商店 | 规则数 | 依据 |
|---|---|---|---|
| `app-store-listing-compliance` | Apple App Store | 43 | App Review Guidelines、DPLA Schedule 2 披露、EU DSA 交易者信息、年龄分级、5.1.2(i) 第三方 AI 数据共享 |
| `play-store-compliance` | Google Play | 37 | Developer Program Policies（Data safety、订阅、AI 生成内容、用户数据、欺骗行为等）及政策截止日期 |

## 它做什么

1. **取数**（确定性脚本，仅 Python 标准库）：商店页 HTML（美区 + 一个欧盟店面）、iTunes Lookup / Data safety 页、隐私标签、隐私政策与条款页。原始响应全部落盘，每个请求记一行日志。
2. **判定**：能由脚本直接得出的规则由脚本给结论；需要语义判断的交给 LLM，按规则库逐条判。
3. **闸门**：每条证据必须是已抓取原文里的逐字子串；`不符合` 必须有正面证据；抓取失败算「未检查」，绝不算通过。
4. **报告**：结论 → 阻断项 → 疑似违规 → 即将到期 → 无法核实。

结论取值：`符合` / `不符合` / `无法从外部判断` / `不适用`。

## 安装

```bash
git clone https://github.com/shiftu/store-compliance-skills.git
cp -R store-compliance-skills/app-store-listing-compliance ~/.hermes/skills/
cp -R store-compliance-skills/play-store-compliance ~/.hermes/skills/
hermes skills list | grep compliance
```

依赖：`python3`、`hermes`（判定这一步通过 `hermes chat` 调模型，provider 与模型见 `scripts/run_app.sh` 顶部变量）。

> `~/.hermes/skills/` 下任何位置如果已有同名 skill，`hermes -s <name>` 会报 `unknown_skill`。

## 使用

```bash
# Apple：传数字 App ID
~/.hermes/skills/app-store-listing-compliance/scripts/run_app.sh 1234567890 runs ExampleApp

# Google Play：传包名
~/.hermes/skills/play-store-compliance/scripts/run_app.sh com.example.app runs ExampleApp
```

输出在 `runs/<slug>/`：`listing.json`、`script_verdicts.json`、`verdicts.json`、`report.md`、`_raw/`。
单独跑闸门：`scripts/check_run.py runs <slug>`。

## 规则库

- 每条规则带官方原文引文，`scripts/verify_quotes.py` 校验引文逐字出现在 `rules/sources/` 的原文快照里。
- `scripts/validate_rules.py` 做结构校验；`scripts/refresh_sources.sh` 重抓官方页并列出受影响的规则。
- 规则库 `verified_on` 超过 60 天时，报告首行会标注「规则库可能过期」。

## 已知局限

- 判的是公开证据，不是审核结果；需要安装包或后台才能确认的条款只会给 `无法从外部判断`。
- LLM 判定在两次运行之间会有少量差异，`不符合` 结论请人工复核证据。
- 未抓取商店截图里的文字，未抓取 Play 内购价格。
- `rules/sources/` 是 Apple 与 Google 官方政策页的快照，版权归各自所有，仅用于引文校验。
