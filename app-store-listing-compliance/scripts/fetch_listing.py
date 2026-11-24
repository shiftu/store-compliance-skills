#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_listing.py — 确定性取数：把商店页与政策页抓成可回放的快照 + 解析后的字段。

用法：
  fetch_listing.py <app_id|package|store_url> <out_dir> [--countries us,de] [--slug S] [--timeout 45]

产出（<out_dir> 由调用方指定）：
  <out_dir>/_logs/fetch_<YYYY-MM-DD>.jsonl     每次 HTTP 请求一行（ts/tool/url/status/used_for）
  <out_dir>/<slug>/_raw/<slug>_*.html|json      原始响应
  <out_dir>/<slug>/_raw/<slug>_*.txt            同一响应的可见文本（去掉 script/style 后的逐字文本）
  <out_dir>/<slug>/listing.json                 解析字段，每个字段带来源文件
  <out_dir>/<slug>/script_verdicts.json         route=script 且脚本能直接定论的规则（LLM 只判其余的）

设计约束：
  * 只用标准库（urllib / html.parser / re / json），不依赖 bs4 / lxml / markdownify。
  * 不做 LLM 调用、不做判定猜测：解析不到的字段写 NOT_CHECKED，结论留给上层。
  * 商店页 404 → listing.json 里 status=delisted，退出码仍为 0。
"""
import argparse
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
PLAY_COOKIE = "CONSENT=YES+cb"
BLOCK_TAGS = {"br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "section",
              "summary", "dt", "dd", "td", "th", "article", "header", "footer", "ul", "ol", "table"}
DROP_TAGS = {"script", "style", "noscript", "svg", "template"}


# ---------------------------------------------------------------- HTML 工具
class _Text(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in DROP_TAGS:
            self.skip += 1
        elif tag in BLOCK_TAGS:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in DROP_TAGS and self.skip:
            self.skip -= 1
        elif tag in BLOCK_TAGS:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


class _Links(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.links, self.cur, self.buf = [], None, []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.cur = dict(attrs).get("href")
            self.buf = []

    def handle_endtag(self, tag):
        if tag == "a" and self.cur is not None:
            self.links.append((self.cur, re.sub(r"\s+", " ", "".join(self.buf)).strip()))
            self.cur, self.buf = None, []

    def handle_data(self, data):
        if self.cur is not None:
            self.buf.append(data)


def visible_text(raw):
    """去 script/style 后的可见文本：保留文字本身与换行，不折叠引文可用的空格。"""
    p = _Text()
    try:
        p.feed(raw)
    except Exception:
        pass
    s = "".join(p.out).replace("\u00a0", " ").replace("\u200b", "")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip() + "\n"


def links_of(raw):
    p = _Links()
    try:
        p.feed(raw)
    except Exception:
        pass
    return [(html.unescape(h or ""), t) for h, t in p.links]


def slugify(s, fallback="app"):
    s = unicodedata.normalize("NFKD", s or "")
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return (s or fallback)[:48]


def line_after(text, label, maxlines=3):
    """取 label 之后的第一批非空行（Apple 页的信息行是「标签\\n值」）。"""
    i = text.find(label)
    if i < 0:
        return None
    tail = text[i + len(label):].split("\n")
    got = []
    for ln in tail[:maxlines]:
        ln = ln.strip()
        if ln:
            got.append(ln)
    return got or None


def rx1(pattern, text, flags=re.S):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None


# ---------------------------------------------------------------- HTTP + 日志
class Fetcher:
    def __init__(self, out_dir, date, timeout=45):
        self.out_dir, self.date, self.timeout = out_dir, date, timeout
        self.requests = 0
        self.log_path = os.path.join(out_dir, "_logs", "fetch_%s.jsonl" % date)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log(self, url, status, used_for, note=""):
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "tool": "fetch",
               "query_or_url": url, "status": status, "used_for": used_for}
        if note:
            rec["note"] = note
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def get(self, url, dest, used_for, cookie=None, retries=1):
        """返回 {http, final_url, body, bytes}；网络层失败时 http=None。"""
        self.requests += 1
        headers = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
        if cookie:
            headers["Cookie"] = cookie
        body, http_code, final = None, None, url
        for attempt in range(retries + 1):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    body = r.read()
                    http_code = getattr(r, "status", r.getcode())
                    final = r.geturl()
                break
            except urllib.error.HTTPError as e:
                http_code = e.code
                try:
                    body = e.read()
                except Exception:
                    body = b""
                final = url
                if e.code in (403, 429) and attempt < retries:
                    time.sleep(2.0 + attempt)
                    continue
                break
            except Exception as e:                                   # 网络/超时
                if attempt < retries:
                    time.sleep(1.5 + attempt)
                    continue
                self.log(url, "blocked", used_for, "network: %s" % e.__class__.__name__)
                return {"http": None, "final_url": url, "body": b"", "bytes": 0}

        status = "ok" if http_code and 200 <= http_code < 300 else (
            "delisted" if http_code in (404, 410) else "blocked")
        self.log(url, status, used_for, "http %s" % http_code)
        if body is None:
            body = b""
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        mode = "wb"
        with open(dest, mode) as fh:
            fh.write(body)
        return {"http": http_code, "final_url": final, "body": body, "bytes": len(body)}

    @staticmethod
    def write_text(dest, raw):
        txt = visible_text(raw)
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(txt)
        return txt


# ---------------------------------------------------------------- Apple
def apple_collect(fx, app_id, slug, countries, app_dir):
    raw_dir = os.path.join(app_dir, "_raw")
    os.makedirs(raw_dir, exist_ok=True)
    listing = {"store": "apple_app_store", "input": app_id, "slug": slug,
               "status": "ok", "countries": countries, "app": {}, "fields": {},
               "links": {}, "evidence_files": [], "missing": [], "notes": []}
    lookups = {}
    for cc in countries:
        url = "https://itunes.apple.com/lookup?id=%s&country=%s" % (app_id, cc)
        f = os.path.join(raw_dir, "%s_itunes_%s.json" % (slug, cc))
        r = fx.get(url, f, "iTunes Lookup (%s)" % cc)
        try:
            data = json.loads(r["body"].decode("utf-8", "ignore") or "{}")
        except ValueError:
            data = {}
        lookups[cc] = data
        listing["evidence_files"].append(
            {"file": "_raw/%s_itunes_%s.json" % (slug, cc), "url": url, "kind": "lookup_api"})

    us = (lookups.get("us") or {}).get("results") or []
    if not us:
        for cc, d in lookups.items():
            if d.get("results"):
                us = d["results"]
                listing["notes"].append("US Lookup 无结果，字段取自 %s 店面" % cc)
                break
    if not us:
        listing["status"] = "delisted"
        listing["notes"].append("iTunes Lookup 在所有店面 resultCount=0：应用已下架或 id 有误")
        return listing
    a = us[0]

    def field(name, value, src, how, group="app"):
        listing[group][name] = value
        listing["fields"][name] = {"value": value, "source": src, "from": how}

    field("name", a.get("trackName"), "_raw/%s_itunes_us.json" % slug, "trackName")
    field("subtitle", None, None, None)
    field("developer", a.get("artistName"), "_raw/%s_itunes_us.json" % slug, "artistName")
    field("seller", a.get("sellerName"), "_raw/%s_itunes_us.json" % slug, "sellerName")
    field("bundle_id", a.get("bundleId"), "_raw/%s_itunes_us.json" % slug, "bundleId")
    field("version", a.get("version"), "_raw/%s_itunes_us.json" % slug, "version")
    field("updated", str(a.get("currentVersionReleaseDate", ""))[:10],
          "_raw/%s_itunes_us.json" % slug, "currentVersionReleaseDate")
    field("price", a.get("formattedPrice"), "_raw/%s_itunes_us.json" % slug, "formattedPrice")
    field("category", (a.get("genres") or [None])[0], "_raw/%s_itunes_us.json" % slug, "genres[0]")
    field("rating_api", a.get("averageUserRating"), "_raw/%s_itunes_us.json" % slug, "averageUserRating")
    field("rating_count", a.get("userRatingCount"), "_raw/%s_itunes_us.json" % slug, "userRatingCount")
    field("age_rating_api", a.get("contentAdvisoryRating"), "_raw/%s_itunes_us.json" % slug,
          "contentAdvisoryRating（旧字段，以产品页为准）")
    field("advisories", a.get("advisories"), "_raw/%s_itunes_us.json" % slug, "advisories")
    field("description", a.get("description"), "_raw/%s_itunes_us.json" % slug, "description")
    field("seller_url", a.get("sellerUrl"), "_raw/%s_itunes_us.json" % slug, "sellerUrl")
    field("screenshots", len(a.get("screenshotUrls") or []), "_raw/%s_itunes_us.json" % slug,
          "len(screenshotUrls)")

    # 应用自述单独落盘：声明类规则（医疗/博彩/强制评分等）只看这段，不混入「App 隐私」数据类别
    desc_f = os.path.join(raw_dir, "%s_description.txt" % slug)
    with open(desc_f, "w", encoding="utf-8") as fh:
        fh.write((a.get("description") or "").strip() + "\n")
    listing["description_file"] = "_raw/%s_description.txt" % slug
    listing["evidence_files"].append({"file": listing["description_file"],
                                      "url": "https://itunes.apple.com/lookup?id=%s&country=us" % app_id,
                                      "kind": "description"})

    # 产品页：每个店面一份 HTML + 可见文本
    for cc in countries:
        url = "https://apps.apple.com/%s/app/id%s" % (cc, app_id)
        raw_f = os.path.join(raw_dir, "%s_appstore_%s.html" % (slug, cc))
        r = fx.get(url, raw_f, "App Store 产品页 (%s)" % cc)
        if r["http"] in (404, 410):
            if cc == "us":
                listing["status"] = "delisted"
                listing["notes"].append("us 产品页 404：应用已下架或 id/地区不匹配")
            # 下架本身要留证据：写一份 http_status 快照，判定时只能引它
            st_f = os.path.join(raw_dir, "%s_appstore_%s.status" % (slug, cc))
            with open(st_f, "w", encoding="utf-8") as fh:
                fh.write("HTTP %s\n%s\n" % (r["http"], url))
            listing["evidence_files"].append(
                {"file": "_raw/%s_appstore_%s.status" % (slug, cc), "url": url, "kind": "http_status"})
            continue
        if not r["body"]:
            listing["missing"].append("appstore_%s_page" % cc)
            continue
        txt_f = os.path.join(raw_dir, "%s_appstore_%s.txt" % (slug, cc))
        text = fx.write_text(txt_f, r["body"].decode("utf-8", "ignore"))
        listing["evidence_files"].append(
            {"file": "_raw/%s_appstore_%s.txt" % (slug, cc), "url": url, "kind": "store_page"})
        raw = r["body"].decode("utf-8", "ignore")
        page = {"cc": cc, "url": url, "text_file": "_raw/%s_appstore_%s.txt" % (slug, cc)}
        page["age_rating"] = rx1(r"Age Rating\s*\n\s*(\d+\+)", text)
        page["iap_flag"] = bool(re.search(r"In.[Aa]pp Purchases\s*\n\s*Yes", text))
        m = re.search(r"In-App Purchases\s*\n(?:Yes\s*\n)?(.*?)(?:\nLearn More|\nCopyright)", text, re.S)
        page["iap_items"] = [x.strip() for x in (m.group(1).split("\n") if m else []) if x.strip()][:20]
        m = re.search(r"\nContains\n(.*?)(?:\nIn-App Purchases|\nLanguages|\nInformation)", text, re.S)
        page["contains"] = [x.strip() for x in (m.group(1).split("\n") if m else []) if x.strip()][:10]
        i = text.find("App Privacy")
        page["privacy_label"] = text[i:i + 2500] if i >= 0 else None
        page["seller_line"] = line_after(text, "Seller", 1)
        page["subtitle"] = None
        lines = [x.strip() for x in text.split("\n") if x.strip()]
        if len(lines) > 1 and a.get("trackName") in lines[:3]:
            page["subtitle"] = lines[lines.index(a.get("trackName")) + 1]
        links = links_of(raw)
        page["links"] = {}
        for href, label in links:
            key = None
            low = (href or "").lower()
            if "apple.com/legal" in low or "policies.google" in low:
                continue
            if re.search(r"privacy|privacypolicy|privacy-policy", low) and key is None:
                key = "privacy"
            elif re.search(r"eula|terms|termsofuse|terms-of-use", low) and key is None:
                key = "eula"
            if key and key not in page["links"]:
                page["links"][key] = href
        listing.setdefault("pages", {})[cc] = page
        if cc == "us":
            if page["subtitle"]:
                field("subtitle", page["subtitle"], page["text_file"], "产品页副标题行")
            field("age_rating", page["age_rating"], page["text_file"], "产品页 Age Rating 行")
            field("contains", page["contains"], page["text_file"], "产品页 Contains 行")
            field("iap_items", page["iap_items"], page["text_file"], "产品页 In-App Purchases 区")
            field("privacy_label_text", (page["privacy_label"] or "")[:1200], page["text_file"],
                  "产品页 App Privacy 段")

    us_page = (listing.get("pages") or {}).get("us") or {}
    eu = [cc for cc in countries if cc != "us"]
    eu_page = (listing.get("pages") or {}).get(eu[0]) if eu else None
    if eu_page:
        field("trader_block", {
            "cc": eu_page["cc"],
            "has_anbieter": bool(re.search(r"\bAnbieter\b", open(
                os.path.join(app_dir, eu_page["text_file"]), encoding="utf-8").read())),
            "has_duns": bool(re.search(r"DUNS", open(
                os.path.join(app_dir, eu_page["text_file"]), encoding="utf-8").read())),
        }, eu_page["text_file"], "EU 店面「Weitere Infos / Anbieter」块")

    # 隐私政策 / 条款 / 支持页
    link_src = us_page.get("links", {})
    targets = [("privacy", link_src.get("privacy"), "隐私政策页"),
               ("eula", link_src.get("eula") or "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/",
                "许可协议 / EULA 页"),
               ("support", link_src.get("support"), "App 支持页")]
    for kind, url, label in targets:
        entry = {"url": url, "present": bool(url), "http": None, "file": None}
        if url:
            ext = ".pdf" if url.lower().split("?")[0].endswith(".pdf") else ".html"
            raw_f = os.path.join(raw_dir, "%s_%s%s" % (slug, kind, ext))
            r = fx.get(url, raw_f, label)
            entry["http"] = r["http"]
            entry["pdf"] = ext == ".pdf"
            if r["body"] and ext == ".html":
                txt_f = os.path.join(raw_dir, "%s_%s.txt" % (slug, kind))
                fx.write_text(txt_f, r["body"].decode("utf-8", "ignore"))
                entry["file"] = "_raw/%s_%s.txt" % (slug, kind)
                listing["evidence_files"].append(
                    {"file": entry["file"], "url": url, "kind": kind})
            elif r["body"]:
                entry["file"] = "_raw/%s_%s%s" % (slug, kind, ext)
                listing["evidence_files"].append(
                    {"file": entry["file"], "url": url, "kind": kind})
        else:
            listing["missing"].append(kind)
        listing["links"][kind] = entry
    return listing


# ---------------------------------------------------------------- Play
def play_collect(fx, package, slug, countries, app_dir):
    raw_dir = os.path.join(app_dir, "_raw")
    os.makedirs(raw_dir, exist_ok=True)
    listing = {"store": "google_play", "input": package, "slug": slug, "status": "ok",
               "countries": countries, "app": {}, "fields": {}, "links": {},
               "evidence_files": [], "missing": [], "notes": [], "pages": {}}
    hl = {"us": "en", "de": "de", "gb": "en", "fr": "fr", "br": "pt", "jp": "ja"}
    gl = {"us": "US", "de": "DE", "gb": "GB", "fr": "FR", "br": "BR", "jp": "JP"}
    for cc in countries:
        url = ("https://play.google.com/store/apps/details?id=%s&hl=%s&gl=%s"
               % (package, hl.get(cc, "en"), gl.get(cc, cc.upper())))
        raw_f = os.path.join(raw_dir, "%s_play_%s.html" % (slug, cc))
        r = fx.get(url, raw_f, "Play 商店页 (%s)" % cc, cookie=PLAY_COOKIE)
        if r["http"] in (404, 410):
            listing["status"] = "delisted"
            listing["notes"].append("%s 商店页 404：应用已下架或包名变更（已下架是结论，不是抓取故障）" % cc)
            with open(os.path.join(raw_dir, "%s_play_%s.status" % (slug, cc)), "w",
                      encoding="utf-8") as fh:
                fh.write("HTTP %s\n%s\n" % (r["http"], url))
            listing["evidence_files"].append(
                {"file": "_raw/%s_play_%s.status" % (slug, cc), "url": url, "kind": "http_status"})
            continue
        if not r["body"]:
            listing["missing"].append("play_%s_page" % cc)
            continue
        txt_f = os.path.join(raw_dir, "%s_play_%s.txt" % (slug, cc))
        text = fx.write_text(txt_f, r["body"].decode("utf-8", "ignore"))
        listing["evidence_files"].append(
            {"file": "_raw/%s_play_%s.txt" % (slug, cc), "url": url, "kind": "store_page"})
        raw = r["body"].decode("utf-8", "ignore")
        page = {"cc": cc, "url": url, "text_file": "_raw/%s_play_%s.txt" % (slug, cc)}
        page["title"] = rx1(r"<h1[^>]*>(.*?)</h1>", raw)
        if page["title"]:
            page["title"] = html.unescape(re.sub(r"<[^>]+>", "", page["title"])).strip()
        page["developer"] = rx1(r'/store/apps/developer\?id=[^"]*"[^>]*>(?:<[^>]+>)*([^<]+)<', raw)
        lines = [x.strip() for x in text.split("\n") if x.strip()]
        if page["title"] in lines:
            k = lines.index(page["title"])
            if not page["developer"] and k + 1 < len(lines):
                page["developer"] = lines[k + 1]
        page["rating"] = rx1(r"([0-9]\.[0-9])star", text) or rx1(r"([0-9],[0-9])star", text)
        page["rating_count"] = rx1(r"star\s*\n?\s*([\d.,]+[KMB]?)\s*reviews", text)
        page["downloads"] = rx1(r"\n([\d.,]+[KMB]?\+)\nDownloads", text)
        page["updated"] = rx1(r"Updated on\n([A-Z][a-z]{2} \d{1,2}, \d{4})", text)
        page["iap_flag"] = "In-app purchases" in text
        page["content_rating"] = (rx1(r"\n(Teen|Everyone|Mature|Adults only)\b", text)
                                  or rx1(r"Rated for (\d+\+)", text))
        page["interactive_elements"] = [x for x in ("Users Interact", "Shares Location",
                                                    "In-App Purchases", "User-Generated Content")
                                        if x in text]
        # 「App support / About the developer」块：网页、电话、邮箱、地址
        i = text.find("App support")
        block = text[i:i + 700] if i >= 0 else ""
        page["support"] = {
            "email": rx1(r"Support email\n([\w.+-]+@[\w.-]+)", block),
            "phone": rx1(r"Phone number\n(\+?[\d*(][\d*()\s-]{5,})", block),
            "address": rx1(r"About the developer\n[^\n]+\n[^\n]*@[^\n]*\n([^\n]+)", block),
            "website": rx1(r"\nWebsite\n((?:https?://)?[a-z0-9.-]+\.[a-z]{2,}[^\n]*)", block),
        }
        links = links_of(raw)
        page["links"], page["link_labels"] = {}, {}
        for href, label in links:
            low = (href or "").lower()
            if not href or href.startswith("/") or "google.com" in low or "gstatic" in low:
                continue
            if "privacy" in low and "privacy" not in page["links"]:
                page["links"]["privacy"] = href
                page["link_labels"]["privacy"] = label
            elif re.search(r"terms|tos|eula", low) and "terms" not in page["links"]:
                page["links"]["terms"] = href
                page["link_labels"]["terms"] = label
        i = text.find("Data safety")
        page["data_safety_summary"] = text[i:i + 400] if i >= 0 else None
        m = re.search(r"\nAbout this app\n(.*?)(?:\nData safety\n|\nApp support\n|\nRatings and reviews\n|\nUpdated on\n)", text, re.S)
        page["description"] = (m.group(1).strip() if m else "")
        listing["pages"][cc] = page

    us_page = listing["pages"].get("us") or {}
    if listing["status"] == "delisted":
        return listing
    src = "_raw/%s_play_us.txt" % slug
    app = listing["app"]
    app["name"] = us_page.get("title")
    app["developer"] = us_page.get("developer")
    app["rating"] = us_page.get("rating")
    app["rating_count"] = us_page.get("rating_count")
    app["downloads"] = us_page.get("downloads")
    app["updated"] = us_page.get("updated")
    app["iap"] = us_page.get("iap_flag")
    app["content_rating"] = us_page.get("content_rating")
    for k, v in app.items():
        listing["fields"][k] = {"value": v, "source": src}

    # Data safety 页（每个店面一份）
    for cc in countries:
        url = ("https://play.google.com/store/apps/datasafety?id=%s&hl=%s&gl=%s"
               % (package, hl.get(cc, "en"), gl.get(cc, cc.upper())))
        raw_f = os.path.join(raw_dir, "%s_datasafety_%s.html" % (slug, cc))
        r = fx.get(url, raw_f, "Play Data safety (%s)" % cc, cookie=PLAY_COOKIE)
        if not r["body"]:
            listing["missing"].append("datasafety_%s" % cc)
            continue
        txt_f = os.path.join(raw_dir, "%s_datasafety_%s.txt" % (slug, cc))
        text = fx.write_text(txt_f, r["body"].decode("utf-8", "ignore"))
        listing["evidence_files"].append(
            {"file": "_raw/%s_datasafety_%s.txt" % (slug, cc), "url": url, "kind": "data_safety"})
        i = text.find("Data safety Here")
        body = text[i:i + 4000] if i >= 0 else text[:4000]
        listing["pages"][cc]["data_safety"] = {"file": "_raw/%s_datasafety_%s.txt" % (slug, cc),
                                               "http": r["http"], "text": body[:3000],
                                               "sections": {
                                                   "shared": "Data shared" in body,
                                                   "collected": "Data collected" in body,
                                                   "security": "Security practices" in body},
                                               "categories": sorted(set(re.findall(
                                                   r"\n([A-Z][A-Za-z ]{3,40}?)\n[^\n]*expand_more", body)))[:20]}
        if cc == "us":
            listing["fields"]["data_safety"] = {
                "value": listing["pages"][cc]["data_safety"]["sections"],
                "source": listing["pages"][cc]["data_safety"]["file"]}

    # 开发者信息页
    dev = app.get("developer")
    if dev:
        page = listing["pages"].get("us") or {}
        listing["fields"]["developer_block"] = {
            "value": {"name": dev, "address_or_contact": bool(re.search(
                r"[\w.+-]+@[\w-]+\.[\w.]+", open(os.path.join(app_dir, src), encoding="utf-8").read()))},
            "source": src}

    # 应用自述单独落盘（声明类规则只看这段）
    desc = (listing["pages"].get("us") or {}).get("description") or ""
    desc_f = os.path.join(raw_dir, "%s_description.txt" % slug)
    with open(desc_f, "w", encoding="utf-8") as fh:
        fh.write(desc.strip() + "\n")
    if desc.strip():
        listing["description_file"] = "_raw/%s_description.txt" % slug
        listing["evidence_files"].append({"file": listing["description_file"],
                                          "url": (listing["pages"]["us"] or {}).get("url", ""),
                                          "kind": "description"})
    else:
        listing["missing"].append("description")
    # 隐私政策 / 条款页
    us_page = listing["pages"].get("us") or {}
    for kind, url, label in (("privacy", us_page.get("links", {}).get("privacy"), "隐私政策页"),
                             ("terms", us_page.get("links", {}).get("terms"), "服务条款页")):
        entry = {"url": url, "present": bool(url), "http": None, "file": None, "pdf": False}
        if url:
            ext = ".pdf" if url.lower().split("?")[0].endswith(".pdf") else ".html"
            raw_f = os.path.join(raw_dir, "%s_%s%s" % (slug, kind, ext))
            r = fx.get(url, raw_f, label)
            entry["http"], entry["pdf"] = r["http"], ext == ".pdf"
            if r["body"]:
                if ext == ".html":
                    txt_f = os.path.join(raw_dir, "%s_%s.txt" % (slug, kind))
                    fx.write_text(txt_f, r["body"].decode("utf-8", "ignore"))
                    entry["file"] = "_raw/%s_%s.txt" % (slug, kind)
                else:
                    entry["file"] = "_raw/%s_%s%s" % (slug, kind, ext)
                listing["evidence_files"].append({"file": entry["file"], "url": url, "kind": kind})
        else:
            listing["missing"].append(kind)
        listing["links"][kind] = entry
    return listing


# ---------------------------------------------------------------- 脚本可判的规则
def ev(file, find=None, absent=None, note=None):
    d = {"file": file}
    if find is not None:
        d["find"] = find
    if absent is not None:
        d["absent"] = absent
    if note:
        d["note"] = note
    return d


def V(verdict, conf, evidence, note):
    return {"verdict": verdict, "confidence": conf, "evidence": evidence, "note": note}


def _page_text(app_dir, listing, cc="us"):
    p = (listing.get("pages") or {}).get(cc) or {}
    f = p.get("text_file")
    if not f:
        return None, None
    return f, open(os.path.join(app_dir, f), encoding="utf-8").read()


def _desc_text(app_dir, listing):
    """应用自述（描述正文）——声明类规则只在描述里看，避免把「App 隐私」数据类别当宣称。"""
    f = listing.get("description_file")
    if f and os.path.exists(os.path.join(app_dir, f)):
        return f, open(os.path.join(app_dir, f), encoding="utf-8").read()
    return _page_text(app_dir, listing)


def _has(text, *pats):
    for p in pats:
        if re.search(p, text, re.I):
            return True
    return False


def check_name_len(app_dir, listing):
    f, text = _page_text(app_dir, listing)
    name = listing["app"].get("name") or ""
    if not f or not name:
        return None
    if len(name) <= 30:
        return V("符合", "高", [ev(f, find=name)], "商店标题 %d 字符（≤30），标题本身不含价格。" % len(name))
    return V("不符合", "高", [ev(f, find=name)],
             "商店标题 %d 字符，超过 2.3.7 的 30 字符上限。" % len(name))


def check_age_rating(app_dir, listing):
    f, text = _page_text(app_dir, listing)
    rating = (listing["app"].get("age_rating") or "").strip()
    if not f or not rating:
        return None
    api = str(listing["app"].get("age_rating_api") or "")
    extra = ("Lookup 旧字段为 %s，产品页（新体系）为 %s，按页面判；问卷答案是否如实填写外部不可见。"
             % (api, rating)) if api and api != rating else "分级问卷答案是否如实填写外部不可见。"
    return V("符合", "中", [ev(f, find=rating)], "产品页分级行存在：%s。%s" % (rating, extra))


def check_rating_form(app_dir, listing):
    """分级取值是否落在新体系（4+/9+/13+/16+/18+）——问卷答案本身外部不可见。"""
    f, text = _page_text(app_dir, listing)
    rating = listing["app"].get("age_rating") or ""
    if not f:
        return None
    if not rating:
        return V("不符合", "高", [ev(f, absent="Age Rating", note="产品页没有 Age Rating 行，分级属性缺失")],
                 "产品页未出现 Age Rating 行，分级属性可能未填。")
    ok = rating in ("4+", "9+", "13+", "16+", "18+")
    return V("符合" if ok else "无法从外部判断", "中", [ev(f, find=rating)],
             "分级取值 %s %s 2026-11 新分级体系的枚举；分级问卷里两个新增描述项（Dating / Shared Location）"
             "是否作答需后台核对。" % (rating, "落在" if ok else "不在"))


def check_support_link(app_dir, listing):
    f, text = _page_text(app_dir, listing)
    if not f:
        return None
    sup = (listing.get("links") or {}).get("support") or {}
    if sup.get("present") and sup.get("http") == 200:
        return V("符合", "中", [ev(f, find="App Support")],
                 "产品页存在 App Support 入口，URL=%s（HTTP 200）。" % sup.get("url"))
    return V("无法从外部判断", "中",
             [ev(f, absent="App Support", note="产品页文本中没有 App Support 行；可能是渲染丢行，不能据此判违规")],
             "产品页文本未出现 App Support 行（页脚另有 Support 字样），无法排除服务端渲染丢行，需人工在浏览器确认。")


def check_privacy_link(app_dir, listing):
    f, text = _page_text(app_dir, listing)
    priv = (listing.get("links") or {}).get("privacy") or {}
    if not f:
        return None
    if not priv.get("present"):
        return V("无法从外部判断", "中",
                 [ev(f, absent="Privacy Policy", note="页面文本未见隐私政策行；渲染丢行与真缺失无法区分")],
                 "产品页未见隐私政策链接，需浏览器/后台核对。")
    if priv.get("http") != 200:
        return V("不符合", "高", [ev(f, find="Privacy Policy")],
                 "产品页有隐私政策链接，但目标页 HTTP=%s（非 200）。" % priv.get("http"))
    pol_file = priv.get("file")
    named = False
    if pol_file:
        body = open(os.path.join(app_dir, pol_file), encoding="utf-8").read().lower()
        named = (listing["app"].get("name") or "").split(":")[0].strip().lower()[:6] in body
    return V("符合", "高", [ev(f, find="Privacy Policy")],
             "产品页有隐私政策链接，目标页 HTTP=200，快照见 %s；政策正文是否点名本 App：%s。"
             % (pol_file, "是" if named else "否（通用模板写法，需人工确认是否覆盖本 App）"))


def check_dsa_trader(app_dir, listing):
    tb = listing["fields"].get("trader_block", {})
    v = tb.get("value") or {}
    f = tb.get("source") or "_raw/%s_appstore_us.txt" % listing["slug"]
    if not f:
        return None
    if v.get("has_anbieter"):
        return V("符合", "高", [ev(f, find="Anbieter")],
                 "EU 店面（%s）产品页出现「Anbieter」交易者块%s。"
                 % (v.get("cc"), "，含 DUNS" if v.get("has_duns") else "（未见 DUNS 行）"))
    return V("不符合", "中", [ev(f, find="Weitere Infos")],
             "EU 店面产品页未见「Anbieter」交易者信息块，DSA 第 30(2) 条要求交易者信息在商品页展示。")


def check_kids_category(app_dir, listing):
    f, text = _page_text(app_dir, listing)
    cat = (listing["app"].get("category") or "")
    if not f:
        return None
    if cat.lower() == "kids":
        return V("无法从外部判断", "中", [ev(f, find="Kids")], "应用属 Kids 分类，链接与内购限制需实机核对。")
    return V("不适用", "高", [ev(f, absent="\nKids\n", note="分类行为 %s，未进入 Kids 分类" % cat)],
             "应用分类为 %s，不在 Kids 分类，1.3 的儿童分类限制不适用。" % cat)


def check_age_restriction(app_dir, listing):
    f, text = _page_text(app_dir, listing)
    rating = listing["app"].get("age_rating") or ""
    if not f or not rating:
        return None
    if rating == "18+":
        return V("不适用", "高", [ev(f, find="Age Rating")],
                 "产品页分级已是 18+，4.7.5 针对「超出分级的软件」的年龄限制前提不成立。")
    return V("无法从外部判断", "低", [ev(f, find=rating)],
             "分级为 %s，是否含超出该分级的内容需实机确认。" % rating)


def check_random_chat(app_dir, listing):
    f, text = _desc_text(app_dir, listing)
    if not f:
        return None
    hit = _has(text, r"random chat", r"anonymous chat", r"chat roulette", r"random video chat",
               r"stranger", r"random match")
    if hit:
        m = re.search(r"(random chat|anonymous chat|chat roulette|random video chat|stranger|random match)", text, re.I)
        return V("无法从外部判断", "中", [ev(f, find=m.group(1))],
                 "商店页出现随机/匿名聊天表述，1.2 适用；过滤/举报/屏蔽是否落地需安装包或实机。")
    return V("不适用", "中", [ev(f, absent="random chat", note="商店页无随机/匿名聊天表述，1.2 的该分支不适用")],
             "商店页与描述未见随机/匿名聊天功能表述，1.2 随机聊天分支前提不成立。")


def check_gambling(app_dir, listing):
    f, text = _desc_text(app_dir, listing)
    if not f:
        return None
    hit = _has(text, r"real money", r"cash prize", r"lottery ticket", r"sports betting", r"casino")
    if hit:
        m = re.search(r"(real money|cash prize|lottery ticket|sports betting|casino)", text, re.I)
        return V("无法从外部判断", "中", [ev(f, find=m.group(1))],
                 "商店页出现真钱博彩/彩票相关表述，牌照与地域限制需后台与法务材料核对。")
    return V("不适用", "高", [ev(f, absent="real money", note="商店页与描述无真钱博彩/彩票表述")],
             "未见真钱博彩或彩票功能表述，5.3.4 前提不成立。")


def check_medical(app_dir, listing):
    f, text = _desc_text(app_dir, listing)
    if not f:
        return None
    hit = _has(text, r"\bdiagnos(?:e|es|ed|is|ing)\b", r"medical device", r"prescription")
    if hit:
        m = re.search(r"(\bdiagnos(?:e|es|ed|is|ing)\b|medical device|prescription)", text, re.I)
        return V("无法从外部判断", "中", [ev(f, find=m.group(1))],
                 "商店页出现医疗/诊断类表述，声明是否可验证需医学材料与实机。")
    return V("不适用", "中", [ev(f, absent="medical device", note="商店页无医疗/诊断类表述")],
             "商店页与描述无医疗测量或诊断声明，1.4.1 前提不成立。")


def check_force_rate(app_dir, listing):
    f, text = _desc_text(app_dir, listing)
    if not f:
        return None
    m = re.search(r"(rate us (?:to|before|for) (?:unlock|continue|use)|5[- ]star to unlock|"
                  r"leave a (?:5[- ]star )?review to (?:unlock|continue))", text, re.I)
    if m:
        return V("不符合", "高", [ev(f, find=m.group(1))],
                 "描述中出现以评分/评论换取功能解锁的表述，属 3.2.2(x) 禁止的强制评分。")
    return V("符合", "中", [ev(f, absent="5-star to unlock", note="描述中未见以评分换解锁的表述")],
             "描述与商店页未见强制评分/评论/下载其他应用的表述。")


def check_complete(app_dir, listing):
    f, text = _desc_text(app_dir, listing)
    if not f:
        return None
    m = re.search(r"(lorem ipsum|placeholder text|coming soon\.{0,3}$|TODO)", text, re.I | re.M)
    if m:
        return V("不符合", "高", [ev(f, find=m.group(1))], "商店页出现占位文本「%s」。" % m.group(1))
    return V("符合", "中", [ev(f, absent="lorem ipsum", note="商店页文本无占位内容")],
             "商店页未见占位文本或未完成内容。")


def check_other_platforms(app_dir, listing):
    f, text = _desc_text(app_dir, listing)
    if not f:
        return None
    m = re.search(r"(Google Play|Play Store|Android app|Samsung Galaxy Store)", text)
    if m:
        return V("不符合", "中", [ev(f, find=m.group(1))],
                 "商店页文本出现其他平台名「%s」；2.3.10 禁止在元数据中提及其他平台或商店（需确认是否在描述正文）。" % m.group(1))
    return V("符合", "高", [ev(f, absent="Google Play", note="产品页与描述未出现其他平台名")],
             "产品页与描述未出现其他平台或商店名称。")


def check_iap_only(app_dir, listing):
    f, text = _page_text(app_dir, listing)
    if not f:
        return None
    iap = listing["app"].get("iap_items") or []
    ext = re.search(r"(stripe\.com|paypal\.com|checkout\.|buy now on our website)", text, re.I)
    if ext:
        return V("不符合", "中", [ev(f, find=ext.group(1))],
                 "商店页出现站外支付入口，数字内容解锁须走 IAP（3.1.1）。")
    if iap:
        return V("符合", "中", [ev(f, find="In-App Purchases")],
                 "页面申报 In-App Purchases（%d 项，含 %s），未见站外支付入口。" % (len(iap), iap[0][:24]))
    return V("无法从外部判断", "低", [ev(f, absent="In-App Purchases", note="页面未申报内购，也未见站外支付；是否有付费内容需实机")],
             "页面未申报内购，无法判断是否存在付费解锁。")


def check_play_title(app_dir, listing):
    f, text = _page_text(app_dir, listing)
    name = listing["app"].get("name") or ""
    if not f or not name:
        return None
    problems = []
    if len(name) > 30:
        problems.append("%d 字符 >30" % len(name))
    if re.search(r"[#＃]\s*1\b|top rated|best app|No\.\s*1", name, re.I):
        problems.append("含排名宣称")
    if sum(1 for c in name if ord(c) > 0x1F000) > 0:
        problems.append("含 emoji")
    if name.isupper() and len(name) > 3:
        problems.append("全大写")
    if problems:
        return V("不符合", "高", [ev(f, find=name)], "标题「%s」命中：%s。" % (name, "；".join(problems)))
    return V("符合", "高", [ev(f, find=name)],
             "标题「%s」%d 字符，无 emoji / 排名宣称 / 全大写。" % (name, len(name)))


def check_play_privacy(app_dir, listing):
    f, text = _page_text(app_dir, listing)
    priv = (listing.get("links") or {}).get("privacy") or {}
    if not f:
        return None
    if not priv.get("present"):
        return V("不符合", "中", [ev(f, absent="privacy", note="商店页无可点击的隐私政策链接（第三方域名）")],
                 "Play 页未找到应用自己的隐私政策链接（只找到 Google 站内链接，不算）。")
    if priv.get("http") != 200:
        return V("不符合", "高", [ev(f, find="privacy")],
                 "隐私政策链接存在但目标页 HTTP=%s。" % priv.get("http"))
    if priv.get("pdf"):
        return V("不符合", "中", [ev(f, find="privacy")], "隐私政策以 PDF 提供，不满足可访问性要求。")
    label = ((listing.get("pages") or {}).get("us", {}).get("link_labels") or {}).get("privacy") or "Data safety"
    if label not in text:
        label = "Data safety"
    return V("符合", "高", [ev(f, find=label)],
             "商店页有应用自有隐私政策链接 %s，HTTP=200（应用内是否另有入口需实机）。" % priv.get("url"))


def check_data_safety(app_dir, listing):
    ds = (listing["fields"].get("data_safety") or {}).get("value")
    src = (listing["fields"].get("data_safety") or {}).get("source")
    if not ds or not src:
        return V("无法从外部判断", "中", [ev("_raw/%s_play_us.txt" % listing["slug"], absent="Data safety",
                                          note="未取到 Data safety 页")],
                 "Data safety 页未取到，需后台核对。")
    if not (ds.get("shared") or ds.get("collected")):
        return V("无法从外部判断", "中", [ev(src, find="Data safety")],
                 "Data safety 页存在但没有可解析的数据类别，需后台核对表单。")
    return V("符合", "中", [ev(src, find="Data safety")],
             "Data safety 页已声明 shared=%s / collected=%s；表单是否完整准确需 Play Console 核对。"
             % (ds.get("shared"), ds.get("collected")))


def check_play_rating(app_dir, listing):
    f, text = _page_text(app_dir, listing)
    rating = listing["app"].get("content_rating")
    if not f or not rating:
        return None
    priv = (listing.get("links") or {}).get("privacy") or {}
    pol_file = priv.get("file")
    pol_text = open(os.path.join(app_dir, pol_file), encoding="utf-8").read() if pol_file else ""
    m = re.search(r"(?:intended for adults|adults aged 18|18 (?:years|and over)|for adults only)", pol_text, re.I)
    teen = rating in ("Teen",)
    if m and teen:
        return V("不符合", "高",
                 [ev(f, find=rating), ev(pol_file, find=m.group(0))],
                 "IARC 分级为 %s，而隐私政策自述「%s」；分级与内容/受众矛盾，需重做内容分级问卷。"
                 % (rating, m.group(0)))
    return V("符合", "中", [ev(f, find=rating)],
             "IARC 分级为 %s，未发现与政策自述年龄的明显冲突；问卷答案是否如实需后台核对。" % rating)


def check_play_families(app_dir, listing):
    f, text = _page_text(app_dir, listing)
    if not f:
        return None
    if _has(text, r"Designed for Families"):
        return V("无法从外部判断", "中", [ev(f, find="Designed for Families")],
                 "页面标注 Designed for Families，儿童隐私与广告限制需后台核对。")
    return V("不适用", "高", [ev(f, absent="Designed for Families", note="页面无家庭计划/Designed for Families 标注")],
             "应用未加入 Designed for Families 计划，Families 政策前提不成立。")


def check_play_health(app_dir, listing):
    f, text = _page_text(app_dir, listing)
    if not f:
        return None
    if not _has(text, r"health", r"medical", r"therapy", r"mental", r"symptom"):
        return V("不适用", "中", [ev(f, absent="medical device", note="页面无健康/医疗表述")],
                 "商店页与描述无健康或医疗表述，健康政策前提不成立。")
    if _has(text, r"not a medical device", r"consult (?:a|your) (?:doctor|physician)", r"professional help"):
        return V("符合", "中", [ev(f, find="consult")], "有健康表述且含免责/就医提示。")
    return V("不符合", "中", [ev(f, find="health")],
             "出现健康表述但描述中未见「非医疗器械」或提示就医的免责声明（GP-HEALTH-02）。")


def check_play_billing(app_dir, listing):
    f, text = _page_text(app_dir, listing)
    if not f:
        return None
    ext = re.search(r"(stripe\.com|paypal\.com|checkout\.|buy on our website)", text, re.I)
    if ext:
        return V("不符合", "中", [ev(f, find=ext.group(1))], "商店页出现站外支付入口，数字商品须走 Play 结算。")
    if listing["app"].get("iap"):
        return V("符合", "中", [ev(f, find="In-app purchases")],
                 "页面申报 In-app purchases，未见站外支付入口。")
    return V("无法从外部判断", "低", [ev(f, absent="In-app purchases", note="页面未申报内购")],
             "页面未申报内购，是否有付费数字商品需实机。")


def check_play_age_gate(app_dir, listing):
    """随机/匿名聊天、约会类应用须屏蔽未成年人：先看是否属该类，再看分级。"""
    f, text = _desc_text(app_dir, listing)
    rating = listing["app"].get("content_rating") or ""
    if not f:
        return None
    m = re.search(r"(dating app|anonymous chat|random chat|meet (?:new )?strangers|"
                  r"video chat with strangers|flirt with)", text, re.I)
    if not m:
        return V("不适用", "中", [ev(f, absent="anonymous chat", note="描述中无匿名/随机聊天或约会类表述")],
                 "描述未见匿名/随机聊天或约会类功能，年龄屏蔽义务的前提不成立（AI 角色对话不属于匿名真人聊天）。")
    if rating in ("Mature", "Adults only", "18+"):
        return V("符合", "中", [ev(f, find=m.group(1))],
                 "属匿名/随机聊天或约会类，分级为 %s（已按成人内容处理）。" % rating)
    page_f, _ = _page_text(app_dir, listing)
    return V("不符合", "中", [ev(f, find=m.group(1)), ev(page_f, find=rating)],
             "属匿名/随机聊天或约会类，但分级为 %s；须在应用内屏蔽未成年人或上调分级。" % rating)


APPLE_CHECKS = {
    "ASRG-2.3.7-NAME": check_name_len,
    "ASRG-2.3.6-AGE-RATING": check_age_rating,
    "ASRG-AGE-RATING-FORM": check_rating_form,
    "ASRG-1.5-SUPPORT": check_support_link,
    "ASRG-5.1.1i-PRIVACY": check_privacy_link,
    "ASRG-DSA-TRADER": check_dsa_trader,
    "ASRG-1.3-KIDS": check_kids_category,
    "ASRG-4.7.5-AGE": check_age_restriction,
    "ASRG-1.2-RANDOM-CHAT": check_random_chat,
    "ASRG-5.3.4-GAMBLING": check_gambling,
    "ASRG-1.4.1-MEDICAL": check_medical,
    "ASRG-3.2.2x-FORCE-RATE": check_force_rate,
    "ASRG-2.1-COMPLETE": check_complete,
    "ASRG-2.3.10-OTHERPLATFORMS": check_other_platforms,
    "ASRG-3.1.1-IAP": check_iap_only,
}

PLAY_CHECKS = {
    "GP-META-01-TITLE": check_play_title,
    "GP-UD-01-PRIVACY": check_play_privacy,
    "GP-UD-02-DATA-SAFETY": check_data_safety,
    "GP-RATE-01-IARC": check_play_rating,
    "GP-FAM-01-FAMILIES": check_play_families,
    "GP-HEALTH-02-DISCLAIMER": check_play_health,
    "GP-HEALTH-01-CLAIMS": check_play_health,
    "GP-PAY-01-BILLING": check_play_billing,
    "GP-AGE-01-BLOCK-MINORS": check_play_age_gate,
}


def build_script_verdicts(app_dir, listing, catalog_path):
    checks = APPLE_CHECKS if listing["store"] == "apple_app_store" else PLAY_CHECKS
    cat = json.load(open(catalog_path, encoding="utf-8"))
    out, skipped = {}, []
    for r in cat["rules"]:
        rid = r["id"]
        route = r.get("route")
        routes = route if isinstance(route, list) else [route]
        if r.get("status") == "upcoming" or "script" not in routes:
            continue
        fn = checks.get(rid)
        if not fn:
            skipped.append(rid)
            continue
        try:
            res = fn(app_dir, listing)
        except Exception as e:                       # 脚本自身出错 → 交回 LLM
            skipped.append(rid)
            listing["notes"].append("check %s failed: %s" % (rid, e))
            continue
        if not res:
            skipped.append(rid)
            continue
        out[rid] = res
    return out, skipped


# ---------------------------------------------------------------- 入口
def detect_store(target):
    t = target.strip()
    if re.match(r"^\d{6,}$", t):
        return "apple", t
    m = re.search(r"apps\.apple\.com/.*?/id(\d+)", t)
    if m:
        return "apple", m.group(1)
    m = re.search(r"itunes\.apple\.com/.*?id=(\d+)", t)
    if m:
        return "apple", m.group(1)
    m = re.search(r"[?&]id=([A-Za-z0-9_.]+)", t)
    if m and "play.google" in t:
        return "play", m.group(1)
    if re.match(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z0-9_]+){2,}$", t):
        return "play", t
    return None, t


def main():
    ap = argparse.ArgumentParser(description="Fetch a store listing + policy pages into a replayable snapshot.")
    ap.add_argument("target", help="Apple trackId / Play package / 商店 URL")
    ap.add_argument("out_dir")
    ap.add_argument("--countries", default="us,de", help="逗号分隔店面，如 us,de（默认 us,de）")
    ap.add_argument("--slug", default=None)
    ap.add_argument("--timeout", type=int, default=45)
    a = ap.parse_args()

    store, ident = detect_store(a.target)
    if not store:
        print("cannot tell store from %r (expect a numeric Apple id or a Play package)" % a.target,
              file=sys.stderr)
        return 2
    date = time.strftime("%Y-%m-%d")
    countries = [c.strip().lower() for c in a.countries.split(",") if c.strip()]
    fx = Fetcher(a.out_dir, date, a.timeout)
    slug = a.slug
    app_dir_probe = os.path.join(a.out_dir, slug) if slug else None
    if not slug:
        # 先用 id 建临时目录名，取到应用名后不改（保持 4 款样本目录名可预测）
        slug = ident.replace(".", "-")
    app_dir = os.path.join(a.out_dir, slug)
    os.makedirs(os.path.join(app_dir, "_raw"), exist_ok=True)

    if store == "apple":
        listing = apple_collect(fx, ident, slug, countries, app_dir)
    else:
        listing = play_collect(fx, ident, slug, countries, app_dir)

    listing["fetched_on"] = date
    listing["requests"] = fx.requests
    listing["log"] = os.path.relpath(fx.log_path, a.out_dir)

    catalog = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "rules", "apple_rules.json" if store == "apple" else "play_rules.json")
    if not os.path.exists(catalog):                     # 跨店同一份脚本时按目录名兜底
        want = "apple_rules.json" if store == "apple" else "play_rules.json"
        cand = [os.path.join(os.path.dirname(catalog), f) for f in os.listdir(os.path.dirname(catalog))
                if f.endswith("_rules.json")]
        catalog = cand[0] if len(cand) == 1 else os.path.join(os.path.dirname(catalog), want)
    script_v, skipped = ({}, [])
    if os.path.exists(catalog):
        try:
            cat_store = json.load(open(catalog, encoding="utf-8")).get("catalog")
        except Exception:
            cat_store = None
        if cat_store != ("apple_app_store" if store == "apple" else "google_play"):
            print("[fetch_listing] 规则库与本店不匹配（%s），跳过脚本判定" % cat_store)
            catalog = None
    if listing["status"] != "delisted" and catalog and os.path.exists(catalog):
        script_v, skipped = build_script_verdicts(app_dir, listing, catalog)
        listing["script_rules_done"] = sorted(script_v)
        listing["script_rules_skipped"] = sorted(skipped)

    with open(os.path.join(app_dir, "listing.json"), "w", encoding="utf-8") as fh:
        json.dump(listing, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(app_dir, "script_verdicts.json"), "w", encoding="utf-8") as fh:
        json.dump(script_v, fh, ensure_ascii=False, indent=2)

    print("[fetch_listing] store=%s id=%s slug=%s status=%s requests=%d script_verdicts=%d"
          % (store, ident, slug, listing["status"], fx.requests, len(script_v)))
    if listing.get("missing"):
        print("[fetch_listing] 未取到：%s" % ", ".join(listing["missing"]))
    if listing.get("notes"):
        for n in listing["notes"]:
            print("[fetch_listing] note: %s" % n)
    print("[fetch_listing] 目录：%s" % app_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
