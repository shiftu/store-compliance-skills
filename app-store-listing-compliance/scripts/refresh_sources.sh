#!/usr/bin/env bash
# refresh_sources.sh —— 重抓规则库引用的官方页，核对每条规则的 quote 是否仍逐字存在。
#
# 用法： scripts/refresh_sources.sh [--keep]
#   默认只核对、不落盘；--keep 把新抓正文另存到 rules/sources/<store>/_refetch/（不覆盖快照）。
#
# 判定口径：版面/导航的差异不算变化（快照是 bs4 按 selector 抓的，重抓是整页去标签，
# 两者必然不同）。只有「规则里的 quote 在新页面里找不到」才算条款变了 —— 那才是要人处理的事。
# 有 quote 失配 → 退出码 1，提示改 quote 与 verified_on。
set -uo pipefail

SKILL_DIR=$(cd "$(dirname "$0")/.." && pwd)
SRC_DIR="$SKILL_DIR/rules/sources"
KEEP=""
[[ "${1:-}" == "--keep" ]] && KEEP=1

[[ -d "$SRC_DIR" ]] || { echo "没有 $SRC_DIR"; exit 1; }

python3 - "$SKILL_DIR" "$SRC_DIR" "$KEEP" <<'PY'
import glob, json, os, re, sys
import urllib.request
from html.parser import HTMLParser

skill_dir, src_dir, keep = sys.argv[1], sys.argv[2], sys.argv[3]
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
BLOCK = {"br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4", "section", "dt", "dd",
         "td", "th", "article", "ul", "ol", "table", "summary"}
DROP = {"script", "style", "noscript", "svg", "template"}


class Text(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in DROP:
            self.skip += 1
        elif tag in BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in DROP and self.skip:
            self.skip -= 1
        elif tag in BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def extract(raw):
    p = Text()
    try:
        p.feed(raw)
    except Exception:
        pass
    s = "".join(p.out).replace("\u00a0", " ").replace("\u200b", "")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def norm(s):
    s = s.replace("\u00a0", " ").replace("\u200b", "")
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-"), ("…", "...")):
        s = s.replace(a, b)
    s = s.lower()
    s = re.sub(r"[#*_`>\[\]()|~]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


cat = None
for p in glob.glob(os.path.join(skill_dir, "rules", "*_rules.json")):
    cat = json.load(open(p, encoding="utf-8"))
if not cat:
    sys.exit("找不到 rules/*_rules.json")

by_url = {}
for r in cat["rules"]:
    u = (r.get("source_url") or "").rstrip("/")
    if u:
        by_url.setdefault(u, []).append(r)

files = sorted(glob.glob(os.path.join(src_dir, "*", "*.md")))
missing, failed, ok = [], [], 0
for f in files:
    head = open(f, encoding="utf-8").read(800)
    m = re.search(r"source: (\S+)", head)
    if not m:
        continue
    url = m.group(1).rstrip("/")
    rules = by_url.get(url) or []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read().decode("utf-8", "ignore")
        body = norm(extract(raw))
    except Exception as e:
        failed.append((os.path.relpath(f, src_dir), "%s: %s" % (e.__class__.__name__, e)))
        continue
    bad = [r for r in rules if r.get("quote") and norm(r["quote"]) not in body]
    if bad:
        missing.append((os.path.relpath(f, src_dir), url, [r["id"] for r in bad]))
    else:
        ok += 1
    if keep:
        store = os.path.basename(os.path.dirname(f))
        d = os.path.join(src_dir, store, "_refetch")
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, os.path.basename(f).replace(".md", "") + "_refetched.txt")
        open(out, "w", encoding="utf-8").write("source: %s\nfetched: auto\n\n%s\n" % (url, extract(raw)))

print("== 核对 %d 份官方快照（规则库 verified_on = %s）" % (len(files), cat.get("verified_on")))
print("   引文仍在原页面：%d 份" % ok)
for name, err in failed:
    print("   FAIL     %s — %s" % (name, err))
for name, url, ids in missing:
    print("   QUOTE-X  %s" % name)
    print("            受影响规则（quote 在新页面找不到）：%s" % ", ".join(ids))
    print("            处理：读 %s 确认条款是否改写 → 更新 quote 与 verified_on → 重跑 verify_quotes.py" % url)
if not missing and not failed:
    print("   所有引文仍逐字存在于官方页；无需改规则库")
sys.exit(1 if missing else 0)
PY
RC=$?
if [[ $RC -ne 0 ]]; then
  echo "[refresh_sources] 有条款原文变化或抓取失败，先处理再采信现有结论"
fi
exit $RC
