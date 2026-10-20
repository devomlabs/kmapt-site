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

def layout(title, desc, body, path, noindex=False, wide=False, extra_head=""):
    full_title = f"{title} | {site['brand']}" if path != "/" else title
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
<meta property="og:type" content="website">
<meta property="og:locale" content="ko_KR">
<meta property="og:site_name" content="{html.escape(site['brand'])}">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{DOMAIN}{path}">
{robots}
{extra_head}
<link rel="stylesheet" href="/assets/doc.css">
<script src="/assets/doc.js"></script>
</head>
<body>
<header class="site-head"><div class="wrap">
<a class="brand" href="/">{html.escape(site['brand'])}</a>
<nav class="site-nav"><a href="/terms/">이용약관</a><a href="/privacy/">개인정보처리방침</a><a href="/support/">문의</a></nav>
</div></header>
<main class="{'landing' if wide else 'wrap'}">
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


SHOTS = ROOT / "src" / "assets" / "shots"

ICONS = {
 "deals": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 21V8l8-5 8 5v13h-6v-6h-4v6H4z" fill="currentColor"/></svg>',
 "community": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h14a3 3 0 0 1 3 3v8a3 3 0 0 1-3 3h-7l-5 4v-4H5a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3z" fill="currentColor"/><circle cx="8" cy="11" r="1.4" fill="var(--accent)"/><circle cx="12" cy="11" r="1.4" fill="var(--accent)"/><circle cx="16" cy="11" r="1.4" fill="var(--accent)"/></svg>',
 "poll": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="11" width="4" height="9" rx="1" fill="currentColor"/><rect x="10" y="4" width="4" height="16" rx="1" fill="currentColor"/><rect x="16" y="8" width="4" height="12" rx="1" fill="currentColor"/></svg>',
 "alerts": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a6 6 0 0 0-6 6v4l-2 3h16l-2-3V9a6 6 0 0 0-6-6z" fill="currentColor"/><path d="M10 19a2 2 0 0 0 4 0z" fill="currentColor"/></svg>',
}

def mock(kind):
    """폰 화면 안쪽. src/assets/shots/<kind>.png 가 있으면 실제 스크린샷, 없으면 임시 화면."""
    if (SHOTS / f"{kind}.png").exists():
        return f'<img src="/assets/shots/{kind}.png" alt="" loading="lazy">', False
    t = {
      "deals": ("실거래가",
        '<div class="m-pill">단지 이름을 검색해 보세요</div>'
        + "".join(f'<div class="m-row"><div><i class="m-l w{w}"></i><i class="m-l s"></i></div><b>00.0억</b></div>' for w in (70, 55, 80))
        + '<div class="m-chart"><u style="height:38%"></u><u style="height:52%"></u><u style="height:46%"></u><u style="height:68%"></u><u style="height:60%"></u><u style="height:80%"></u></div>'),
      "community": ("단지 게시판",
        "".join(f'<div class="m-card"><i class="m-l w{w}"></i><i class="m-l s"></i><i class="m-l s w50"></i><span>공감 0 · 댓글 0</span></div>' for w in (75, 60, 70))),
      "poll": ("투표",
        '<div class="m-card"><i class="m-l w80"></i><i class="m-l s w50"></i></div>'
        + "".join(f'<div class="m-opt"><em style="width:{w}%"></em><span>선택지 {n}</span><b>{w}%</b></div>' for n, w in ((1, 60), (2, 30), (3, 10)))),
      "alerts": ("알림 설정",
        '<div class="m-set"><span>중요 공지</span><i class="m-sw on"></i></div>'
        '<div class="m-set"><span>광고성 정보 수신</span><i class="m-sw"></i></div>'
        '<p class="m-note">밤 9시부터 아침 8시까지는 보내지 않아요.</p>'),
    }[kind]
    return f'<div class="m-bar">{t[0]}</div><div class="m-body">{t[1]}</div>', True

FEATURES = [
 ("deals", "우리 단지 실거래가,<br>한눈에 확인해요", "공공 실거래 자료를 단지별로 모아 보여 드려요. 최근 거래와 전월세 흐름을 쉽게 비교해 보세요."),
 ("community", "이웃과 나누는<br>우리 단지 이야기", "게시글과 댓글, 공감으로 단지 소식과 생활 정보를 나눠요. 연락처 노출은 자동으로 걸러내고, 신고와 숨김으로 안전하게 이용할 수 있어요."),
 ("poll", "궁금할 땐<br>투표로 물어보세요", "주차, 시설, 이사 등 이웃의 생각이 궁금한 주제를 투표로 모아 보세요."),
 ("alerts", "관심 단지와<br>꼭 필요한 알림만", "관심 단지를 저장해 두고 중요한 공지를 알림으로 받아요. 광고성 알림은 동의한 경우에만, 밤 9시부터 아침 8시까지는 보내지 않아요."),
]

def landing_page():
    placeholder_used = False
    secs = []
    for i, (kind, title, desc) in enumerate(FEATURES):
        inner, ph = mock(kind)
        placeholder_used |= ph
        secs.append(f"""<section class="feat {'alt' if i % 2 == 0 else ''}" id="{kind}"><div class="inner">
<div class="ico">{ICONS[kind]}</div>
<h2>{title}</h2>
<p>{desc}</p>
<figure class="phone" aria-hidden="true"><div class="screen">{inner}</div></figure>
</div></section>""")
    btn = ('<div class="stores"><span class="store" aria-disabled="true"><small>출시 예정</small>App Store</span>'
           '<span class="store" aria-disabled="true"><small>출시 예정</small>Google Play</span></div>')
    cap = '<p class="cap">* 화면은 이해를 돕기 위한 예시입니다.</p>' if placeholder_used else ""
    body = f"""<section class="hero"><div class="inner">
<div class="mark" aria-hidden="true"><svg viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="var(--accent)"/><path d="M14 52V26l18-12 18 12v26H38V38H26v14z" fill="#1c1c1c"/></svg></div>
<h1>우리 아파트의 모든 이야기,<br>{html.escape(site['brand'])}</h1>
<p>실거래가부터 이웃 이야기까지.<br>우리 단지 소식을 한곳에서 확인해요.</p>
{btn}
</div></section>
{''.join(secs)}
<section class="hero end"><div class="inner">
<h2>우리 단지 이야기,<br>곧 만나요</h2>
{btn}
{cap}
<p class="fine">실거래가 등 부동산 정보는 공공기관이 공개한 자료를 바탕으로 하며, 참고용입니다. 투자·거래 결정에 대한 조언이 아니에요.</p>
</div></section>"""
    head = '<link rel="stylesheet" href="/assets/landing.css">'
    return body, head

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
        if slug == "index":
            lb, lh = landing_page()
            page = layout("김대리네 아파트 - 아파트 실거래가·단지 커뮤니티", meta["desc"], subst(lb), "/", wide=True, extra_head=lh)
            write("index.html", page)
            continue
        page = layout(meta["title"], meta["desc"], subst(body), path or "/404.html", noindex=(path is None))
        if slug == "404":
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
