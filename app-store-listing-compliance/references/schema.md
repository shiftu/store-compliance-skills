# 数据契约：`listing.json` / `verdicts.json`

所有产物都是 UTF-8 JSON（`ensure_ascii=False`）。字段名固定，下游 `render_report.py`、`check_run.py` 直接读，不要改名。

## 1. 目录布局

```
<out_dir>/
  _logs/fetch_<YYYY-MM-DD>.jsonl    每次 HTTP 请求一行（append-only）
  <slug>/
    _raw/                           原始响应 + 可见文本 + prompt.md + llm_output.txt
    listing.json                    取数结果（fetch_listing.py 写）
    script_verdicts.json            route=script 且脚本能定论的条目（fetch_listing.py 写）
    verdicts.json                   全量结论（run_app.sh 合并后写）
    report.md                      五段报告（render_report.py 写）
```

`<slug>` 由 `fetch_listing.py` 决定：Apple 用 trackId（如 `1234567890`），Play 用包名把 `.` 换成 `-`（如 `com-example-app`）。

## 2. `_logs/fetch_<date>.jsonl`

一行一次真实请求，**没有这一行的 URL 不得出现在 `sources[]` 里**：

```json
{"ts":"2026-11-24T01:20:03-0600","tool":"fetch",
 "query_or_url":"https://apps.apple.com/us/app/id1234567890",
 "status":"ok|blocked|empty|delisted","used_for":"App Store 产品页 (us)","note":"http 200"}
```

`check_run.py` 校验：日志行数 ≥ `listing.json.requests`。

## 3. `listing.json`

```json
{
  "store": "apple_app_store",          // 或 google_play
  "input": "1234567890",               // 调用方给的原值
  "slug": "1234567890",
  "status": "ok",                      // ok | delisted（404/410）
  "fetched_on": "2026-11-24",
  "countries": ["us", "de"],
  "requests": 6,
  "log": "_logs/fetch_2026-11-24.jsonl",
  "app": {"name": "...", "developer": "...", "seller": "...", "version": "...",
          "age_rating": "18+", "category": "Lifestyle", "price": "Free",
          "iap_items": ["Weekly $9.99", "..."], "contains": ["Infrequent/Mild ..."]},
  "fields": {"<字段>": {"value": ..., "source": "_raw/xxx.json", "from": "trackName"}},
  "links": {"privacy": {"url": "...", "http": 200, "file": "_raw/..._privacy.txt"},
            "eula":   {...}, "support": {...}},
  "pages": {"us": {"age_rating": "18+", "text_file": "_raw/..._appstore_us.txt", "links": {...}}},
  "evidence_files": [{"file": "_raw/..._appstore_us.txt", "url": "https://...", "kind": "store_page"}],
  "description_file": "_raw/..._description.txt",
  "missing": ["support"],
  "notes": [],
  "script_rules_done": ["ASRG-..."],
  "script_rules_skipped": ["ASRG-..."]
}
```

要点：

- `evidence_files[]` 是**唯一合法的证据白名单**：`verdicts.json.evidence[].file` 必须是其中某个相对路径。
- 取不到的字段写进 `missing[]`，不要填猜测值。若解析彻底失败该字段写字符串 `"NOT_CHECKED"`。
- 产品页 404 → `status=delisted`，退出码 0（下架是结论，不是故障）。
- `fields[*].source` 让「这个数字从哪来」可回查；`app` 是给人和模型看的汇总，`fields` 才是取证用的。

## 4. `script_verdicts.json`

`{ "<rule_id>": {"verdict","confidence","evidence":[...],"note"} }`。只含 `route` 里带 `script` 且脚本解析成功、能直接定论的条目；其余留给模型。`run_app.sh` 会原样并入 `verdicts.json`，**不要手改**。

## 5. `verdicts.json`

```json
{
  "store": "apple_app_store",
  "app": "1234567890",
  "slug": "1234567890",
  "judged_on": "2026-11-24",
  "listing_status": "ok",
  "sources": [{"file": "_raw/...", "url": "...", "kind": "store_page", "external": false}],
  "summary": {
    "符合": 20, "不符合": 2, "无法从外部判断": 8, "不适用": 13,
    "total": 43,                        // 四项之和，不含 upcoming
    "risk": "🔴 高风险",
    "violations_by_severity": {"removal": ["ASRG-..."], "rejection": ["ASRG-..."], "advisory": []},
    "upcoming_excluded": []
  },
  "deadlines": [{"rule_id": "...", "due": "2027-02-01", "todo": "...", "source_url": "..."}],
  "verdicts": [
    {"rule_id": "ASRG-5.1.1i-PRIVACY",
     "verdict": "不符合",              // 符合 | 不符合 | 无法从外部判断 | 不适用
     "confidence": "高",              // 高 | 中 | 低
     "evidence": [{"file": "_raw/x.txt", "find": "逐字片段"},
                  {"file": "_raw/x.txt", "absent": "确认不存在的串", "note": "为何算证据"}],
     "note": "判据一句话",
     "verified_by": "App Store Connect 后台",   // 判不了时写谁能给
     "layers": [{"layer": "public_listing", "verdict": "不符合", "note": "..."}],  // 可选
     "absence_only_violation": false}                              // 仅「该有的缺失」才为 true
  ]
}
```

## 6. 风险等级怎么算（`check_run.py` 重算，写错即 FAIL）

| 条件 | 等级 |
|---|---|
| 有 `不符合` 且其规则 `severity=removal` | 🔴 高风险 |
| 有 `不符合` 且 severity 为 `rejection` / `advisory` | 🟡 有条件 |
| 无 `不符合`，但 `无法从外部判断` 占比 > 40% | ⚪ 待判定（取数能力不足） |
| 无 `不符合`，未知占比 ≤ 40% | 🟢 可上 |

`upcoming` 规则不进计数、不进等级，只进 `deadlines[]`。

## 7. 证据两条铁律

- `find`：必须是 `_raw` 文件里的**逐字连续子串**。比对时不做任何归一化（不折叠空白、不换引号、不剥 markdown）——归一化是假引文的入口。
- `absent`：确认该文件里**没有**这个串，且必须带 `note` 说明「为什么这个缺失构成本条的违反」。`absent` 只能证明「没有」，不能单独证明「错」。
