#!/usr/bin/env bash
# run_app.sh —— 一款 App 的完整判定流水线：取数 → LLM 判 llm 规则 → 合并 → 闸门 → 报告
#
# 用法： run_app.sh <app_id|package> <out_dir> [app 名称] [judge]
#        第 4 参数：judge = 跳过取数、重跑判定；merge = 只重跑合并（llm_output.txt 已有时用）
#
# 环境变量：COUNTRIES(us,de) HERMES_MODEL HERMES_PROVIDER HERMES_REASONING
#           HERMES_MAX_TURNS(80) HERMES_BUDGET(1800) JUDGE_ATTEMPTS(2，漏判时重判的总次数) JUDGE_TIMEOUT(600，单轮判定秒数上限)
#           RENDER_FALLBACK(1，JS 渲染的政策页用 tinyfish 取正文；0 关闭)
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
ATTEMPTS=${JUDGE_ATTEMPTS:-2}
JUDGE_TIMEOUT=${JUDGE_TIMEOUT:-600}

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
KEY = re.compile(r"\bAI\b|artificial intelligence|language model|third[- ]part|service provider|delet|"
                 r"consent|permission|subscri|renew|refund|children|under 1[368]|18 years|track|advertis|"
                 r"location|health|sell", re.I)
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
        rest = t[LIMIT_PER_FILE:]
        keep = [ln for ln in rest.split("\n") if KEY.search(ln)][:40]
        t = t[:LIMIT_PER_FILE] + "\n…（已截断。截断之后命中关键词的行如下，均为原文逐字，可直接引用；其余部分用 grep 读原文件）\n" \
            + "\n".join(keep)
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
A("9. **先读下面的「预抽取事实」。** 那是脚本从原文里机械数出来的（隐私标签申报了哪些类别、政策里点名了哪些 AI 供应商、"
  "Data safety 的删除声明、别的店面是否上架、政策/条款正文有没有取到）。结论不得与它矛盾；要引用它，证据仍指向它标的那个文件。")
A("10. **只在应用内或后台才看得到的要求，一律 `无法从外部判断`**：购买页写没写「付费得到什么」、有没有恢复购买、"
  "应用内删号入口、同意弹窗、年龄门、举报/屏蔽入口。商店描述或政策里没提，不等于应用里没有，不得据此判 `不符合`。")
A("11. **没抓到 ≠ 不存在。** 政策正文未取到、条款页未抓取、某店面 404、截图未采集——这些只能支持 `无法从外部判断`"
  "（或规则前提不成立时的 `不适用`），不能支持 `不符合`。")
A("12. **同一件事只判一次 `不符合`。** 一个事实同时碰到两条规则时，选最贴切的一条判 `不符合`，另一条写 `无法从外部判断` 并在 note 里指向它。")
A("13. 发现的问题只是「披露不够具体」而不是「做了条款禁止的事」时，在该条加 `\"severity_override\": \"advisory\"`"
  "（只能往轻调）。用户评论、论坛帖子只能当线索写进 note，不能作为 `find` 证据。")
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
if listing.get("facts"):
    A("## 预抽取事实（脚本机械抽取，优先于你自己的印象）")
    A("")
    A("```json")
    A(json.dumps(listing["facts"], ensure_ascii=False, indent=1))
    A("```")
    A("")
    if listing.get("notes"):
        A("取数备注：" + "；".join(listing["notes"]))
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
A('    "severity_override": "advisory（可选，仅「披露不够具体」时用）",')
A('    "verified_by": "安装包 / App Store Connect / Play Console / 隐私政策页（判不了时填）" }')
A('] }')
A("```")
A("")
A("必须覆盖全部 %d 个 rule_id：%s" % (len(todo), ", ".join(r["id"] for r in todo)))
open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("[run_app] prompt=%s (%d chars, %d evidence files, %d rules)"
      % (out, len("\n".join(L)), len(files), len(todo)))
PY

# ---------------------------------------------------------------- 3) 判定（函数；漏判时补判）
SKILL_ARGS=()
[[ "$INSTALLED" == "1" ]] && SKILL_ARGS=(-s "$SKILL_NAME")

judge() {   # judge <prompt 文件> <输出文件>
  # 模型接口偶尔会挂住不返回：到时限就杀掉，交给后面的补判轮次
  set +e
  hermes chat --provider "$PROVIDER" -m "$MODEL" --reasoning "$REASONING" \
    ${SKILL_ARGS[@]+"${SKILL_ARGS[@]}"} --query-file "$1" --oneshot -Q \
    --max-turns "$MAXT" --run-budget "$BUDGET" > "$2" 2>&1 &
  local pid=$! waited=0 rc
  while kill -0 "$pid" 2>/dev/null; do
    if [[ $waited -ge $JUDGE_TIMEOUT ]]; then
      echo "[run_app] 判定超过 ${JUDGE_TIMEOUT}s 未返回，终止本轮"
      kill "$pid" 2>/dev/null; sleep 2; kill -9 "$pid" 2>/dev/null
      break
    fi
    sleep 5; waited=$((waited + 5))
  done
  wait "$pid" 2>/dev/null; rc=$?
  set -e
  echo "[run_app] hermes exit=$rc (${waited}s) - log: $2"
}

missing_ids() {
  python3 -c "import json,sys; print(','.join(json.load(open(sys.argv[1],encoding='utf-8')).get('missing_rule_ids') or []))" \
    "$APP_DIR/verdicts.json"
}

# ---------------------------------------------------------------- 4) 合并 verdicts.json（函数）
merge() {
python3 - "$SKILL_DIR" "$APP_DIR" <<'PY'
import glob, json, os, re, sys

skill_dir, app_dir = sys.argv[1:3]
sys.path.insert(0, os.path.join(skill_dir, "scripts"))
from check_run import effective_severity, evidence_errors, expected_risk

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


# 每一轮判定各有一份输出（llm_output.txt、llm_output_2.txt…）；后一轮只补前一轮漏掉的
outs = sorted(glob.glob(os.path.join(app_dir, "_raw", "llm_output*.txt")),
              key=lambda p: (len(os.path.basename(p)), p))
for op in outs:
    raw = open(op, encoding="utf-8", errors="replace").read()
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M)
    best, perr = None, None
    for frag in objects(raw):
        try:
            obj = json.loads(frag)
        except Exception as e:
            perr = perr or ("%s: %s" % (e.__class__.__name__, e))
            continue
        vs = obj.get("verdicts") if isinstance(obj, dict) else None
        if isinstance(vs, list) and (best is None or len(vs) > len(best)):
            best = vs
    if best is None:
        err = err or perr or "输出里没有找到含 verdicts 的 JSON 对象（%s）" % os.path.basename(op)
        continue
    for v in best:
        if isinstance(v, dict) and v.get("rule_id") in rules and v.get("verdict"):
            llm[v["rule_id"]] = v
if llm:
    err = None
if not outs:
    err = "没有模型输出文件"

src_files = {e["file"] for e in listing.get("evidence_files") or []}
ev_cache = {}


def settle(v):
    """证据不过逐字校验的结论不进报告：剔掉坏证据；剔完站不住的结论降为「无法从外部判断」。"""
    good, bad = [], []
    for e in v.get("evidence") or []:
        probe = {"verdict": "符合", "evidence": [e]}
        problems = evidence_errors(app_dir, probe, src_files, ev_cache)
        (bad if problems else good).append((e, problems))
    out = dict(v, evidence=[e for e, _ in good])
    if not bad and not evidence_errors(app_dir, out, src_files, ev_cache):
        return out
    reasons = ["；".join(p) for _, p in bad] or evidence_errors(app_dir, out, src_files, ev_cache)
    still_ok = not evidence_errors(app_dir, out, src_files, ev_cache)
    if still_ok:                       # 剩下的证据仍够支撑原结论
        out["evidence_dropped"] = reasons
        return out
    if v.get("verdict") == "无法从外部判断" and out["evidence"]:
        out["evidence_dropped"] = reasons
        return out
    out.update(verdict="无法从外部判断", confidence="低", demoted_from=v.get("verdict"),
               gate_errors=reasons, absence_only_violation=None,
               note="【自动降级】模型原判「%s」，但给出的证据没通过逐字校验（%s），按未核实处理，需人工复核。原说明：%s"
                    % (v.get("verdict"), reasons[0][:120], v.get("note", "")))
    return out


verdicts, missing = [], []
for rid, r in rules.items():
    if rid in script:
        v = dict(script[rid], rule_id=rid)
    elif rid in llm:
        v = settle(llm[rid])
    else:
        if rid not in upcoming:          # 未生效条款本来就不判，不算漏判
            missing.append(rid)
        continue
    verdicts.append({"rule_id": rid, "verdict": v["verdict"], "confidence": v.get("confidence", "低"),
                     "evidence": v.get("evidence") or [], "note": v.get("note", ""),
                     "verified_by": v.get("verified_by"),
                     "layers": v.get("layers"),
                     "absence_only_violation": v.get("absence_only_violation")})
    for k in ("severity_override", "demoted_from", "gate_errors", "evidence_dropped"):
        if v.get(k):
            verdicts[-1][k] = v[k]
    if verdicts[-1].get("severity_override") not in (None, "rejection", "advisory"):
        verdicts[-1].pop("severity_override")

counts = {"符合": 0, "不符合": 0, "无法从外部判断": 0, "不适用": 0}
vbs = {"removal": [], "rejection": [], "advisory": []}
for v in verdicts:
    if v["rule_id"] in upcoming:
        continue
    counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
    if v["verdict"] == "不符合":
        vbs.setdefault(effective_severity(rules[v["rule_id"]], v), []).append(v["rule_id"])
total = sum(counts.values())
unknown_ratio = (counts["无法从外部判断"] / total) if total else 0.0
risk = expected_risk({k for k, ids in vbs.items() if ids}, unknown_ratio, listing.get("status"))
demoted = [v["rule_id"] for v in verdicts if v.get("demoted_from")]

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
if demoted:
    out["demoted_rule_ids"] = demoted
if err:
    out["llm_parse_error"] = err
if missing:
    out["missing_rule_ids"] = missing
json.dump(out, open(os.path.join(app_dir, "verdicts.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("[run_app] verdicts.json: %d 条（脚本 %d + 模型 %d）%s"
      % (len(verdicts), len(script), len(verdicts) - len(script),
         "；未覆盖 %d 条：%s" % (len(missing), ", ".join(missing)) if missing else ""))
if demoted:
    print("[run_app] 证据未过校验、已自动降级 %d 条：%s" % (len(demoted), ", ".join(demoted)))
if err:
    print("[run_app] 模型输出解析失败：%s" % err)
PY
}

if [[ "$MODE" == "merge" ]]; then
  merge
else
  rm -f "$APP_DIR"/_raw/llm_output*.txt
  echo "[run_app] judge: model=$MODEL reasoning=$REASONING skill=$SKILL_NAME"
  judge "$PROMPT" "$APP_DIR/_raw/llm_output.txt"
  merge
  n=1
  while [[ $n -lt $ATTEMPTS ]]; do
    MISS=$(missing_ids)
    [[ -z "$MISS" ]] && break
    n=$((n + 1))
    echo "[run_app] 漏判 $MISS —— 第 $n 轮只补这些"
    RETRY="$APP_DIR/_raw/prompt_retry_$n.md"
    { cat "$PROMPT"; printf '\n## 补判\n\n上一轮输出漏了下面这些规则。本轮**只输出这些 rule_id** 的结论（格式不变），其余不要重判：%s\n' "$MISS"; } > "$RETRY"
    judge "$RETRY" "$APP_DIR/_raw/llm_output_$n.txt"
    merge
  done
fi

# ---------------------------------------------------------------- 5) 闸门 + 报告
python3 "$SKILL_DIR/scripts/check_run.py" "$OUT" "$SLUG" --pre-render
python3 "$SKILL_DIR/scripts/render_report.py" "$OUT" "$SLUG"
python3 "$SKILL_DIR/scripts/check_run.py" "$OUT" "$SLUG"
