#!/usr/bin/env bash
# run_app.sh —— 一款 App 的完整判定流水线：取数 → LLM 判 llm 规则 → 合并 → 闸门 → 报告
#
# 用法： run_app.sh <app_id|package> <out_dir> [app 名称] [judge]
#        第 4 参数：judge = 跳过取数、重跑判定；merge = 只重跑合并（llm_output.txt 已有时用）
#
# 环境变量：COUNTRIES(us,de) HERMES_MODEL HERMES_PROVIDER HERMES_REASONING
#           HERMES_MAX_TURNS(80) HERMES_BUDGET(1800)
set -euo pipefail

SKILL_DIR=$(cd "$(dirname "$0")/.." && pwd)
SKILL_NAME=$(basename "$SKILL_DIR")

APP=${1:?用法: run_app.sh <app_id|package> <out_dir> [app 名称] [judge]}
OUT=${2:?缺 out_dir}
NAME=${3:-$APP}
MODE=${4:-full}

COUNTRIES=${COUNTRIES:-us,de}
MODEL=${HERMES_MODEL:-deepseek/deepseek-v4.1-flash-1017}
PROVIDER=${HERMES_PROVIDER:-ominigate}
REASONING=${HERMES_REASONING:-high}
MAXT=${HERMES_MAX_TURNS:-80}
BUDGET=${HERMES_BUDGET:-1800}

mkdir -p "$OUT/_logs"

# ---------------------------------------------------------------- 1) 取数
if [[ "$MODE" != "judge" ]]; then
  echo "[run_app] fetch: $APP → $OUT"
  python3 "$SKILL_DIR/scripts/fetch_listing.py" "$APP" "$OUT" --countries "$COUNTRIES"
fi

APP_DIR=$(python3 - "$OUT" "$APP" <<'PY'
import glob, json, os, sys
out, app = sys.argv[1], sys.argv[2]
cands = []
for p in glob.glob(os.path.join(out, "*", "listing.json")):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    if str(d.get("input")) == app:
        cands.append((os.path.getmtime(p), os.path.dirname(p)))
if not cands:
    sys.exit("找不到 %s 的 listing.json，先跑 fetch_listing.py" % app)
print(sorted(cands)[-1][1])
PY
)
SLUG=$(basename "$APP_DIR")
echo "[run_app] app_dir=$APP_DIR"

# 技能只处理自己那一家店：规则库 catalog 字段与 listing.store 必须一致
SKILL_STORE=$(python3 -c "import glob,json,sys,os; p=glob.glob(os.path.join(sys.argv[1],'rules','*_rules.json')); d=json.load(open(p[0],encoding='utf-8')); print(d.get('catalog',''))" "$SKILL_DIR")
APP_STORE=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1],encoding='utf-8'))['store'])" "$APP_DIR/listing.json")
if [[ "$SKILL_STORE" != "$APP_STORE" ]]; then
  echo "[run_app] 店不匹配：skill=$SKILL_STORE app=$APP_STORE（这是 $SKILL_NAME 技能，请用对应技能跑）" >&2
  exit 2
fi

# 是否已安装在 Hermes 的 skills 目录（决定用 -s 还是把 SKILL.md 内联进 prompt）
INSTALLED=0
case "$SKILL_DIR" in "$HOME/.hermes/skills/"*) INSTALLED=1 ;; esac
export INSTALLED

# ---------------------------------------------------------------- 2) 组装 prompt
PROMPT="$APP_DIR/_raw/prompt.md"
python3 - "$SKILL_DIR" "$APP_DIR" "$NAME" "$PROMPT" <<'PY'
import glob, json, os, re, sys

skill_dir, app_dir, app_name, out = sys.argv[1:5]
listing = json.load(open(os.path.join(app_dir, "listing.json"), encoding="utf-8"))
store = listing["store"]
cat_path = os.path.join(skill_dir, "rules",
                        "apple_rules.json" if store == "apple_app_store" else "play_rules.json")
cat = json.load(open(cat_path, encoding="utf-8"))
script = {}
sp = os.path.join(app_dir, "script_verdicts.json")
if os.path.exists(sp):
    script = json.load(open(sp, encoding="utf-8"))

# 交给 LLM 的规则：非 upcoming，且不在脚本已定论之列
todo = [r for r in cat["rules"]
        if r.get("status") != "upcoming" and r["id"] not in script]

LIMIT_PER_FILE = 9000
files, total = [], 0
for e in listing.get("evidence_files") or []:
    rel = e["file"]
    p = os.path.join(app_dir, rel)
    if not os.path.exists(p) or rel.endswith((".html", ".json", ".pdf")):
        continue
    if total > 45000:
        break
    t = open(p, encoding="utf-8", errors="replace").read()
    if len(t) > LIMIT_PER_FILE:
        t = t[:LIMIT_PER_FILE] + "\n…（已截断，需要更多可自行 sed 读取原文件）"
    total += len(t)
    files.append((rel, e.get("url"), t))

L = []
A = L.append
if os.environ.get("INSTALLED") != "1":
    md = open(os.path.join(skill_dir, "SKILL.md"), encoding="utf-8").read()
    A("<!-- 本 skill 未安装到 Hermes skills 目录，SKILL.md 内联在此作为工作规范 -->")
    A(md)
    A("")
    A("---")
    A("")
A("# 任务：商店合规判定（%s / %s）" % (app_name, store))
A("")
A("你要按本 skill 的规则库，对 `%s` 这一款应用逐条判定，输出 JSON。工作目录就是应用目录：`%s`。" % (app_name, app_dir))
A("")
A("## 硬性规则")
A("1. 只判下面「待判定规则」里的 id，一条不漏；已由脚本定论的 %d 条不要再判（也不要在输出里出现）。" % len(script))
A("2. 每条结论的 `evidence` 必须指向给出结论的那个 `_raw` 文件，`find` 必须是从该文件文本里**逐字复制**的连续片段"
  "（不合并空白、不换引号、不加删字、不跨行拼）。下面贴出的文本就是可用的原文；要引用没贴出的部分，"
  "用 `grep -n` 读原文件后再复制，不要凭印象写。")
A("3. 判断不了的写 `无法从外部判断`：需要安装包、实机、商店后台（App Store Connect / Play Console）、"
  "或只有开发者内部材料才能看到的，一律如此，并在 note 里写清缺什么、谁能给。")
A("4. 规则前提不成立（例如应用没有该功能、分类不适用）写 `不适用`，并给证据说明为什么前提不成立"
  "（通常是 `absent`：该文件里确认没有相关表述）。不得用 `符合` 顶替 `不适用`。")
A("5. `不符合` 必须有至少一条 `find` 正面证据。只有「该有的东西缺失」这一种情形，才允许 `find` 为空并设"
  " `\"absence_only_violation\": true`，且在 note 里说明缺失本身如何构成违反。")
A("6. 置信度只用 高 / 中 / 低：原文明确写的判「高」；需要一步推论、或页面渲染可能丢行的判「中」；只能间接推断的判「低」。")
A("7. 只输出一个 JSON 对象，不要 markdown 代码块、不要解释文字。")
A("8. 不要写临时脚本或中间文件（不要 `_draft_*.py`）：直接给最终 JSON。需要核对字符串时用 `grep`。")
A("")
A("## 应用事实（来自 listing.json，可直接引用为证据来源）")
A("")
A("```json")
A(json.dumps({"store": store, "input": listing.get("input"), "status": listing.get("status"),
              "countries": listing.get("countries"), "app": listing.get("app"),
              "links": {k: {"url": (v or {}).get("url"), "http": (v or {}).get("http")}
                        for k, v in (listing.get("links") or {}).items()},
              "missing": listing.get("missing")}, ensure_ascii=False, indent=1))
A("```")
A("")
if listing.get("status") == "delisted":
    A("> 该应用商店页返回 404，`status=delisted`——下架本身就是要报告的结论。此时除下架抓取里的"
      "`HTTP 404` 之外没有任何页面可查，所以：**每条规则一律判 `无法从外部判断`**，"
      "`evidence` 写证据清单里 `kind=http_status` 的那份文件，`find` 用该文件里的 `HTTP 404` 整行；"
      "不得把任何条款判成 `符合`，也不得因为下架就整片写 `不适用`。")
    A("")
if script:
    A("## 脚本已定论的条目（原样保留，不要重判）")
    A("")
    A("| rule_id | verdict | 置信度 | 依据 |")
    A("|---|---|---|---|")
    for rid, v in script.items():
        A("| %s | %s | %s | %s |" % (rid, v["verdict"], v["confidence"],
                                    v["note"].replace("|", "\\|")[:160]))
    A("")

A("## 证据文本（`_raw/` 快照，逐字可引用）")
A("")
for rel, url, t in files:
    A("### `%s`" % rel)
    A("来源：%s" % url)
    A("<<<")
    A(t)
    A(">>>")
    A("")

A("## 待判定规则（共 %d 条）" % len(todo))
A("")
for r in todo:
    A("### %s · %s" % (r["id"], r["title"]))
    A("- 条号：%s ｜ 等级：%s ｜ 可观测层：%s" % (r.get("section"), r.get("severity"),
                                            r.get("observability")))
    A("- 要求：%s" % r.get("requirement"))
    if r.get("quote"):
        A("- 原文：“%s”" % r["quote"])
    if r.get("signals"):
        A("- 公开信号：%s" % r["signals"])
    if r.get("verify"):
        A("- 怎么核：%s" % r["verify"])
    if r.get("false_positive_notes"):
        A("- 防误报：%s" % r["false_positive_notes"])
    A("")

A("## 输出格式")
A("")
A("```json")
A('{ "verdicts": [')
A('  { "rule_id": "ASRG-…",')
A('    "verdict": "符合|不符合|无法从外部判断|不适用",')
A('    "confidence": "高|中|低",')
A('    "evidence": [ {"file": "_raw/xxx.txt", "find": "原文逐字片段"},')
A('                  {"file": "_raw/xxx.txt", "absent": "确认不存在的字符串", "note": "为什么缺失算证据"} ],')
A('    "note": "一句话说清判据",')
A('    "verified_by": "安装包 / App Store Connect / Play Console / 隐私政策页（判不了时填）" }')
A('] }')
A("```")
A("")
A("必须覆盖全部 %d 个 rule_id：%s" % (len(todo), ", ".join(r["id"] for r in todo)))
open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("[run_app] prompt=%s (%d chars, %d evidence files, %d rules)"
      % (out, len("\n".join(L)), len(files), len(todo)))
PY

# ---------------------------------------------------------------- 3) 判定
if [[ "$MODE" != "merge" ]]; then
echo "[run_app] judge: model=$MODEL reasoning=$REASONING skill=$SKILL_NAME"
SKILL_ARGS=()
[[ "$INSTALLED" == "1" ]] && SKILL_ARGS=(-s "$SKILL_NAME")
set +e
hermes chat --provider "$PROVIDER" -m "$MODEL" --reasoning "$REASONING" \
  ${SKILL_ARGS[@]+"${SKILL_ARGS[@]}"} --query-file "$PROMPT" --oneshot -Q \
  --max-turns "$MAXT" --run-budget "$BUDGET" > "$APP_DIR/_raw/llm_output.txt" 2>&1
RC=$?
set -e
set +u
echo "[run_app] hermes exit=$RC - log: $APP_DIR/_raw/llm_output.txt"
set -u
fi   # MODE=merge 时跳过取数与判定，只用已有 _raw/llm_output.txt 重新合并

# ---------------------------------------------------------------- 4) 合并 verdicts.json
python3 - "$SKILL_DIR" "$APP_DIR" <<'PY'
import json, os, re, sys

skill_dir, app_dir = sys.argv[1:3]
listing = json.load(open(os.path.join(app_dir, "listing.json"), encoding="utf-8"))
store = listing["store"]
cat = json.load(open(os.path.join(skill_dir, "rules",
                                  "apple_rules.json" if store == "apple_app_store" else "play_rules.json"),
                     encoding="utf-8"))
rules = {r["id"]: r for r in cat["rules"]}
upcoming = {rid for rid, r in rules.items() if r.get("status") == "upcoming"}
script = {}
if os.path.exists(os.path.join(app_dir, "script_verdicts.json")):
    script = json.load(open(os.path.join(app_dir, "script_verdicts.json"), encoding="utf-8"))

raw = open(os.path.join(app_dir, "_raw", "llm_output.txt"), encoding="utf-8", errors="replace").read()
raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M)
llm, err = {}, None


def objects(s):
    """枚举所有配平的大括号片段（模型输出里常夹带工具调用/diff 噪声）。"""
    i = 0
    while True:
        start = s.find("{", i)
        if start < 0:
            return
        depth, instr, esc = 0, False, False
        for j in range(start, len(s)):
            ch = s[j]
            if instr:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    instr = False
                continue
            if ch == '"':
                instr = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    yield s[start:j + 1]
                    i = j + 1
                    break
        else:
            i = start + 1      # 这个 { 配不平（噪声/diff），从下一个字符继续找，别中断整个扫描


best = None
for frag in objects(raw):
    try:
        obj = json.loads(frag)
    except Exception as e:
        err = err or ("%s: %s" % (e.__class__.__name__, e))
        continue
    vs = obj.get("verdicts") if isinstance(obj, dict) else None
    if isinstance(vs, list) and (best is None or len(vs) > len(best)):
        best = vs
if best is None:
    err = err or "输出里没有找到含 verdicts 的 JSON 对象"
else:
    for v in best:
        if isinstance(v, dict) and v.get("rule_id") in rules:
            llm[v["rule_id"]] = v

verdicts, missing = [], []
for rid, r in rules.items():
    if rid in script:
        v = dict(script[rid], rule_id=rid)
    elif rid in llm:
        v = llm[rid]
    else:
        missing.append(rid)
        continue
    verdicts.append({"rule_id": rid, "verdict": v["verdict"], "confidence": v.get("confidence", "低"),
                     "evidence": v.get("evidence") or [], "note": v.get("note", ""),
                     "verified_by": v.get("verified_by"),
                     "layers": v.get("layers"),
                     "absence_only_violation": v.get("absence_only_violation")})

counts = {"符合": 0, "不符合": 0, "无法从外部判断": 0, "不适用": 0}
vbs = {"removal": [], "rejection": [], "advisory": []}
for v in verdicts:
    if v["rule_id"] in upcoming:
        continue
    counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
    if v["verdict"] == "不符合":
        vbs.setdefault(rules[v["rule_id"]].get("severity"), []).append(v["rule_id"])
total = sum(counts.values())
unknown_ratio = (counts["无法从外部判断"] / total) if total else 0.0
if vbs.get("removal"):
    risk = "🔴 高风险"
elif vbs.get("rejection") or vbs.get("advisory"):
    risk = "🟡 有条件"
else:
    risk = "⚪ 待判定（取数能力不足）" if unknown_ratio > 0.4 else "🟢 可上"

# 即将到期：从规则库的 upcoming 条目 + (Play) policy_deadlines 的时间表合成
dl = []
dpath = os.path.join(skill_dir, "rules", "play_deadlines.json")
if os.path.exists(dpath):
    for d in json.load(open(dpath, encoding="utf-8")).get("deadlines") or []:
        for rid in d.get("rules") or []:
            if rid in upcoming:
                dl.append({"rule_id": rid, "due": d.get("deadline"), "todo": d.get("summary", ""),
                           "source_url": d.get("source") or cat.get("source_index", "")})
for rid in sorted(upcoming):
    if not any(x["rule_id"] == rid for x in dl):
        r = rules[rid]
        m = re.search(r"\d{4}-\d{2}-\d{2}", r.get("effective_or_updated") or "")
        dl.append({"rule_id": rid, "due": m.group(0) if m else "未标注",
                   "todo": r.get("requirement", "")[:300], "source_url": r.get("source_url")})

sources = [{"file": e["file"], "url": e["url"], "kind": e.get("kind"), "external": False}
           for e in listing.get("evidence_files") or []]

out = {"store": store, "app": listing.get("input"), "slug": os.path.basename(app_dir),
       "judged_on": listing.get("fetched_on"), "listing_status": listing.get("status"),
       "sources": sources, "summary": dict(counts, total=total, risk=risk,
                                           violations_by_severity=vbs,
                                           upcoming_excluded=sorted(upcoming)),
       "deadlines": dl, "verdicts": verdicts}
if err:
    out["llm_parse_error"] = err
if missing:
    out["missing_rule_ids"] = missing
json.dump(out, open(os.path.join(app_dir, "verdicts.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("[run_app] verdicts.json: %d 条（脚本 %d + 模型 %d）%s"
      % (len(verdicts), len(script), len(verdicts) - len(script),
         "；未覆盖 %d 条：%s" % (len(missing), ", ".join(missing)) if missing else ""))
if err:
    print("[run_app] 模型输出解析失败：%s" % err)
PY

# ---------------------------------------------------------------- 5) 闸门 + 报告
python3 "$SKILL_DIR/scripts/check_run.py" "$OUT" "$SLUG" --pre-render
python3 "$SKILL_DIR/scripts/render_report.py" "$OUT" "$SLUG"
python3 "$SKILL_DIR/scripts/check_run.py" "$OUT" "$SLUG"
