#!/usr/bin/env python3
"""정적 사이트 빌더. 사용법: python3 build.py  → docs/ 생성 (GitHub Pages: main 브랜치 /docs)

새 약관 버전 추가:
 1) src/terms/YYYY-MM-DD.html (또는 src/privacy/...) 에 새 본문 작성
 2) versions.json 의 해당 배열 '맨 뒤'에 {date, announced, summary} 추가
 3) python3 build.py 실행 → 최신본(/terms/)이 새 버전으로 바뀌고 이전 버전은 /terms/v/날짜/ 에 그대로 남음
 이미 시행된 버전의 본문 파일은 고치지 말 것 (증빙).
"""
import json, shutil, html, re
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
site = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
versions = json.loads((ROOT / "versions.json").read_text(encoding="utf-8"))
op = site["operator"]
DOMAIN = site["domain"]

DOCS = {
    "terms": "이용약관",
    "privacy": "개인정보처리방침",
}

def kdate(s):
    y, m, d = map(int, s.split("-"))
    return f"{y}년 {m}월 {d}일"

def subst(text, extra=None):
    m = {
        "brand": site["brand"], "domain": DOMAIN,
        "operator_name": op["name"], "operator_rep": op["representative"],
        "operator_bizno": op["business_no"], "operator_addr": op["address"],
        "operator_phone": op["phone"], "support_email": op["email"],
        "privacy_officer": op["privacy_officer"],
        "privacy_officer_email": op["privacy_officer_email"],
    }
    if extra: m.update(extra)
    return re.sub(r"\{\{(\w+)\}\}", lambda x: m[x.group(1)], text)

def layout(title, desc, body, path, noindex=False):
    full_title = f"{title} | {site['brand']}" if path != "/" else site["brand"]
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    foot = (
        f'<div class="links"><a href="/terms/">이용약관</a><a href="/privacy/">개인정보처리방침</a>'
        f'<a href="/support/">문의</a><a href="/account-deletion/">계정 삭제 안내</a></div>'
        f'<div>{html.escape(op["name"])} · 대표 {html.escape(op["representative"])} · 사업자등록번호 {op["business_no"]}<br>'
        f'{op["address"]} · 전화 {op["phone"]} · <a href="mailto:{op["email"]}">{op["email"]}</a></div>'
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{DOMAIN}{path}">
{robots}
<link rel="stylesheet" href="/assets/doc.css">
<script src="/assets/doc.js"></script>
</head>
<body>
<header class="site-head"><div class="wrap">
<a class="brand" href="/">{html.escape(site['brand'])}</a>
<nav class="site-nav"><a href="/terms/">이용약관</a><a href="/privacy/">개인정보처리방침</a><a href="/support/">문의</a></nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site-foot"><div class="wrap">{foot}</div></footer>
</body>
</html>
"""

def write(rel, content):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

def parse_page(path):
    head, body = path.read_text(encoding="utf-8").split("\n---\n", 1)
    meta = dict(line.split(": ", 1) for line in head.splitlines())
    return meta, body

def doc_page(kind, v, latest):
    name = DOCS[kind]
    frag = (ROOT / "src" / kind / f"{v['date']}.html").read_text(encoding="utf-8")
    is_latest = v is latest
    opts = []
    for x in reversed(versions[kind]):
        url = f"/{kind}/" if x is latest else f"/{kind}/v/{x['date']}/"
        label = kdate(x["date"]) + (" (현행)" if x is latest else "")
        sel = " selected" if x is v else ""
        opts.append(f'<option value="{url}"{sel}>{label}</option>')
    draft = ('<div class="notice"><strong>초안입니다.</strong> 법률 검토 전 내용이며, 표시된 항목은 확정 후 바뀔 수 있습니다.</div>'
             if site.get("draft") else "")
    old = ("" if is_latest else
           f'<div class="notice">이전 버전의 문서입니다. <a href="/{kind}/">현행 {name} 보기</a></div>')
    body = f"""<h1>{name}</h1>
<p class="meta">{"<span class='badge'>현행</span> " if is_latest else ""}시행일 {kdate(v['date'])} · 공고일 {kdate(v['announced'])}</p>
<div class="ver-bar"><label for="ver-select">버전</label>
<select id="ver-select">{''.join(opts)}</select>
<a href="/{kind}/history/">변경 이력</a></div>
{draft}{old}
{subst(frag, {"effective_date": kdate(v['date'])})}"""
    path = f"/{kind}/" if is_latest else f"/{kind}/v/{v['date']}/"
    return layout(name, f"{site['brand']} {name} ({kdate(v['date'])} 시행)", body, path, noindex=not is_latest)

def history_page(kind):
    name = DOCS[kind]
    latest = versions[kind][-1]
    rows = []
    for x in reversed(versions[kind]):
        url = f"/{kind}/" if x is latest else f"/{kind}/v/{x['date']}/"
        cur = " <span class='badge'>현행</span>" if x is latest else ""
        rows.append(f'<tr><td><a href="{url}">{kdate(x["date"])}</a>{cur}</td><td>{kdate(x["announced"])}</td><td>{html.escape(x["summary"])}</td></tr>')
    body = f"""<h1>{name} 변경 이력</h1>
<p class="meta">날짜를 누르면 그 시점에 시행된 전문을 볼 수 있어요.</p>
<div class="table-scroll"><table><thead><tr><th>시행일</th><th>공고일</th><th>변경 내용</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p><a href="/{kind}/">현행 {name} 보기</a></p>"""
    return layout(f"{name} 변경 이력", f"{site['brand']} {name}의 버전별 이력", body, f"/{kind}/history/")

def main():
    # 삭제 없이 덮어쓰기 (오래된 파일이 남으면 docs/ 에서 직접 정리)
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / "src" / "assets", OUT / "assets", dirs_exist_ok=True)
    urls = ["/"]
    for kind in DOCS:
        vs = versions[kind]
        latest = vs[-1]
        for v in vs:
            if v is latest:
                write(f"{kind}/index.html", doc_page(kind, v, latest))
            write(f"{kind}/v/{v['date']}/index.html", doc_page(kind, v, latest))
        write(f"{kind}/history/index.html", history_page(kind))
        urls += [f"/{kind}/", f"/{kind}/history/"]
    for slug, path in [("index", "/"), ("support", "/support/"), ("account-deletion", "/account-deletion/"), ("404", None)]:
        meta, body = parse_page(ROOT / "src" / "pages" / f"{slug}.html")
        page = layout(meta["title"], meta["desc"], subst(body), path or "/404.html", noindex=(path is None))
        if slug == "index":
            write("index.html", page)
        elif slug == "404":
            write("404.html", page)
        else:
            write(f"{slug}/index.html", page)
            urls.append(path)
    (OUT / "CNAME").write_text("kmapt.com\n")
    (OUT / ".nojekyll").write_text("")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /terms/v/\nDisallow: /privacy/v/\nSitemap: {DOMAIN}/sitemap.xml\n")
    today = date.today().isoformat()
    sm = "".join(f"<url><loc>{DOMAIN}{u}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    print("built", len(list(OUT.rglob('*.html'))), "pages")

main()
