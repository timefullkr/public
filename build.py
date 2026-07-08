# -*- coding: utf-8 -*-
"""제주교육 AI · 공개 문서 사이트 빌드 (자체 완결 HTML + Bloom PDF + 검증).

- 스크립트가 있는 저장소 폴더(ROOT) 기준으로만 동작 → 경로 하드코딩 없음, 어느 PC에서나 실행.
- 문서 목록·사이트 문구는 docs.json 이 단일 소스 — 문서 추가는 docs.json 에 항목 추가 + md 파일 배치.
- 각 .md 를 임베디드 CSS HTML 로 변환하고 index.html(문서 카드 그리드) 생성.
- Bloom 페이지는 Chrome/Edge 헤드리스로 PDF 저장 후 검증(빈 페이지·에러 페이지 차단).

필요: python -m pip install markdown pypdf   /  Chrome 또는 Edge 설치
사용: python build.py
"""
import json
import os
import re
import sys
import subprocess
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parent

META = json.loads((ROOT / "docs.json").read_text(encoding="utf-8"))
SITE = META["site"]
DOCS = META["docs"]

# 마크다운 내부 링크(.md) → 사이트 내 .html 슬러그 (aliases: 과거 파일명도 매핑해 안전)
LINK_MAP = {}
for _d in DOCS:
    LINK_MAP[_d["md"]] = _d["slug"]
    for _a in _d.get("aliases", []):
        LINK_MAP[_a] = _d["slug"]

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

CSS = """
:root{--bg:#ffffff;--fg:#1a1a1a;--muted:#5b6470;--line:#e3e6ea;--accent:#1f6feb;--soft:#f6f8fa;--quote:#f0f4f9}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--fg:#e6edf3;--muted:#9aa4b2;--line:#283039;--accent:#58a6ff;--soft:#161b22;--quote:#12181f}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);
 font-family:"Pretendard Variable","Pretendard",-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic","Apple SD Gothic Neo","Noto Sans KR",sans-serif;
 line-height:1.72;font-size:19px;word-break:keep-all;overflow-wrap:anywhere}
.wrap{max-width:820px;margin:0 auto;padding:32px 22px 80px}
nav.top{max-width:820px;margin:0 auto;padding:12px 22px;border-bottom:1px solid var(--line);font-size:14px}
nav.top a.home{display:inline-flex;align-items:center;gap:10px;color:var(--muted);text-decoration:none}
nav.top a.home:hover{color:var(--accent)}
nav.top img.logo{height:36px;width:auto;display:block;background:#fff;padding:3px 6px;border-radius:6px;border:1px solid var(--line)}
h1{font-size:1.9rem;line-height:1.35;margin:.2em 0 .5em;letter-spacing:-.01em}
h1[align="center"]{margin:.1em 0 .15em}
.lead-sub{color:var(--muted);font-size:1.05rem;font-weight:600;margin:-.2em 0 1.4em;text-align:center}
p[align="center"] sub{vertical-align:baseline;font-size:1.05rem;color:var(--muted);font-weight:600}
p[align="center"]{margin:0 0 1.4em}
h2{font-size:1.4rem;margin:1.8em 0 .5em;padding-bottom:.25em;border-bottom:1px solid var(--line)}
h3{font-size:1.15rem;margin:1.4em 0 .4em}
p{margin:.7em 0}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
ul,ol{padding-left:1.4em;margin:.6em 0}
li{margin:.25em 0}
blockquote{margin:1em 0;padding:.6em 1em;background:var(--quote);border-left:4px solid var(--accent);border-radius:4px}
blockquote p{margin:.4em 0}
code{background:var(--soft);padding:.12em .4em;border-radius:4px;font-size:.9em;
 font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace}
pre{background:var(--soft);padding:14px 16px;border-radius:8px;overflow-x:auto}
pre code{background:none;padding:0}
hr{border:none;border-top:1px solid var(--line);margin:2em 0}
.tablewrap{overflow-x:auto;margin:1em 0}
table{border-collapse:collapse;width:100%;font-size:.94em}
th,td{border:1px solid var(--line);padding:8px 11px;text-align:left;vertical-align:top}
th{background:var(--soft);font-weight:600}
tr:nth-child(even) td{background:color-mix(in srgb,var(--soft) 45%,transparent)}
.foot{max-width:820px;margin:0 auto;padding:24px 22px;color:var(--muted);font-size:13px;border-top:1px solid var(--line)}
.pdflink{display:inline-block;margin:0 0 18px;padding:8px 14px;border:1px solid var(--line);
 border-radius:8px;background:var(--soft);color:var(--fg);font-size:14px;font-weight:600}
.pdflink:hover{border-color:var(--accent);color:var(--accent);text-decoration:none}
.idx-pdf{margin-left:8px;font-size:13px;padding:1px 8px;border:1px solid var(--line);border-radius:12px}
/* index 문서 카드 그리드 */
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;margin:1.6em 0}
.card{border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--soft);display:flex;flex-direction:column;transition:border-color .2s,box-shadow .2s}
.card:hover{border-color:var(--accent);box-shadow:0 4px 18px rgba(0,0,0,.10)}
.card-thumb{display:block;position:relative;aspect-ratio:16/10;overflow:hidden}
.card-thumb img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
/* 복수 썸네일 슬라이드쇼: 기본은 전부 투명, 첫 장만 표시(애니메이션 미지원 대비), 키프레임이 순환 */
.card-thumb.multi img{opacity:0}
.card-thumb.multi img:first-child{opacity:1}
@media (prefers-reduced-motion:reduce){.card-thumb.multi img{animation:none!important;opacity:0}.card-thumb.multi img:first-child{opacity:1}}
.card-body{padding:14px 16px 16px;display:flex;flex-direction:column;gap:8px;flex:1}
.card-title{font-size:1.02rem;line-height:1.45;margin:0;padding:0;border:none}
.card-title a{color:var(--fg)}
.card-title a:hover{color:var(--accent);text-decoration:none}
.card-desc{margin:0;font-size:.86rem;line-height:1.6;color:var(--muted);flex:1}
.card-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.card-actions a{font-size:12.5px;font-weight:600;padding:3px 10px;border:1px solid var(--line);border-radius:999px;background:var(--bg);color:var(--fg)}
.card-actions a:hover{border-color:var(--accent);color:var(--accent);text-decoration:none}
.card-group{margin-left:auto;align-self:center;font-size:12px;color:var(--muted);opacity:.75}
/* 홀수 채움 카드 — 제주교육지표 이미지, 링크·호버 없음 */
.card.filler{align-items:center;justify-content:center;padding:26px;background:#fff}
.card.filler:hover{border-color:var(--line);box-shadow:none}
.card.filler img{width:82%;max-width:340px;height:auto}
@media print{nav.top,.foot,.pdflink{display:none}body{font-size:11pt;font-family:"Malgun Gothic","Apple SD Gothic Neo","Noto Sans KR",sans-serif}.wrap{max-width:none}}
"""

# 복수 썸네일 크로스페이드 키프레임 — docs.json 에 등장하는 장수(N)별로 생성.
# 장당 5초 표시, 0.8초 페이드. 전체 주기 T=5N초, 이미지 i의 delay 는 card() 에서 인라인 지정.
SLIDE_SECS, FADE_SECS = 5.0, 0.8
for _n in sorted({len(_d["thumb"]) for _d in DOCS
                  if isinstance(_d.get("thumb"), list) and len(_d["thumb"]) > 1}):
    _t = SLIDE_SECS * _n
    _p1, _p2, _p3 = (FADE_SECS / _t * 100), (SLIDE_SECS / _t * 100), ((SLIDE_SECS + FADE_SECS) / _t * 100)
    CSS += (f"@keyframes cardfade{_n}{{0%{{opacity:0}}{_p1:.3f}%{{opacity:1}}"
            f"{_p2:.3f}%{{opacity:1}}{_p3:.3f}%{{opacity:0}}100%{{opacity:0}}}}\n"
            f".card-thumb.thumbs-{_n} img{{animation:cardfade{_n} {_t:g}s linear infinite}}\n")

TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="icon" href="logo-jje.jpg">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>{css}</style>
</head>
<body>
<nav class="top"><a class="home" href="index.html" title="제주도교육감직인수위원회 홈"><img class="logo" src="logo-jje.jpg" alt="제주특별자치도교육청"><span>제주도교육감직인수위원회</span></a></nav>
<main class="wrap">
{body}
</main>
<div class="foot">원문 마크다운에서 자동 생성</div>
</body>
</html>
"""

md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "attr_list"])


def convert(md_name):
    text = (ROOT / md_name).read_text(encoding="utf-8")
    for k, v in LINK_MAP.items():
        text = text.replace(k, v)
    md.reset()
    html = md.convert(text)
    html = re.sub(r"<table>", '<div class="tablewrap"><table>', html)
    html = re.sub(r"</table>", "</table></div>", html)
    return html


def find_browser():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def make_pdf(slug, pdf_name):
    browser = find_browser()
    if not browser:
        sys.exit("Chrome/Edge 를 찾지 못했습니다.")
    html_uri = (ROOT / slug).resolve().as_uri()   # file:///C:/... (경로 인코딩 안전)
    pdf_path = ROOT / pdf_name
    subprocess.run(
        [browser, "--headless=new", "--no-sandbox", "--disable-gpu",
         "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", html_uri],
        check=True, capture_output=True)
    # 검증: 정상 PDF는 크고 다중 페이지. 에러 페이지(ERR_FILE_NOT_FOUND)는 1쪽·소용량.
    # (웹폰트 임베드 시 한글 텍스트 추출이 깨질 수 있어 '본문 키워드'는 실패 근거로 쓰지 않음)
    data = pdf_path.read_bytes()
    ok = data[:5] == b"%PDF-" and len(data) > 80000
    pages = "?"
    try:
        from pypdf import PdfReader
        r = PdfReader(str(pdf_path))
        pages = len(r.pages)
        txt = "".join((pg.extract_text() or "") for pg in r.pages)
        if "ERR_FILE" in txt or "cannot be reached" in txt.lower():
            ok = False
        if isinstance(pages, int) and pages < 1:
            ok = False
    except ImportError:
        pass
    print(f"  PDF {pdf_name}: {len(data):,}B, pages={pages}, ok={ok}")
    if not ok:
        sys.exit(f"PDF 검증 실패: {pdf_name} (빈 페이지/에러 페이지 의심)")


def card(d):
    """문서 1건 → 카드 HTML (썸네일 + 제목 + 설명 + 링크 배지).
    thumb 는 문자열(1장 고정) 또는 배열(5초 간격 크로스페이드 순환)."""
    thumb = ""
    thumbs = d.get("thumb")
    if isinstance(thumbs, str):
        thumbs = [thumbs]
    if thumbs:
        if len(thumbs) == 1:
            cls, imgs = "card-thumb", f'<img src="{thumbs[0]}" alt="" loading="lazy">'
        else:
            n, t = len(thumbs), SLIDE_SECS * len(thumbs)
            cls = f"card-thumb multi thumbs-{n}"
            # 이미지 i 는 [5i, 5i+5) 구간에 표시 — 음수 delay 로 위상을 당겨 첫 장이 로드 즉시 보이게
            imgs = "".join(
                f'<img src="{src}" alt="" loading="lazy" '
                f'style="animation-delay:{SLIDE_SECS * i - FADE_SECS - t:.1f}s">'
                for i, src in enumerate(thumbs))
        thumb = (f'<a class="{cls}" href="{d["slug"]}" tabindex="-1" aria-hidden="true">'
                 f'{imgs}</a>')
    actions = [f'<a href="{d["slug"]}">문서</a>']
    if d.get("slides"):
        actions.append(f'<a href="{d["slides"]}">슬라이드</a>')
    if d.get("pdf"):
        actions.append(f'<a href="{d["pdf"]}">PDF</a>')
    if d.get("group"):   # 분과명 — 카드 하단 오른쪽 옅은 글씨
        actions.append(f'<span class="card-group">{d["group"]}</span>')
    return (f'<article class="card">{thumb}<div class="card-body">'
            f'<h2 class="card-title"><a href="{d["slug"]}">{d["title"]}</a></h2>'
            f'<p class="card-desc">{d["desc"]}</p>'
            f'<div class="card-actions">{"".join(actions)}</div>'
            f'</div></article>')


def index_body():
    # 단일 카드 그리드 — 분과명은 각 카드 하단 오른쪽에 표시. 홀수면 교육지표 이미지로 채움.
    cards = "\n".join(card(d) for d in DOCS)
    if len(DOCS) % 2 == 1:
        cards += ('\n<div class="card filler" aria-hidden="true">'
                  '<img src="img/제주교육지표-세로.png" alt="" loading="lazy"></div>')
    intro = f'<p>{SITE["intro"]}</p>\n' if SITE.get("intro") else ""
    return (f'<h1 align="center">{SITE["heading"]}</h1>\n'
            f'<p class="lead-sub">{SITE["subtitle"]}</p>\n'
            f'{intro}'
            f'<div class="cards">\n{cards}\n</div>')


def main():
    for d in DOCS:
        body = convert(d["md"])
        links = []
        if d.get("slides"):
            links.append(f'<a class="pdflink" href="{d["slides"]}">🖥 발표 슬라이드(웹)</a>')
        if d.get("pdf"):
            links.append(f'<a class="pdflink" href="{d["pdf"]}">⬇ PDF로 저장·인쇄</a>')
        if links:
            body = " ".join(links) + "\n" + body
        (ROOT / d["slug"]).write_text(TEMPLATE.format(title=d["title"], css=CSS, body=body), encoding="utf-8")
        print("wrote", d["slug"])
        if d.get("pdf"):
            make_pdf(d["slug"], d["pdf"])

    index_html = TEMPLATE.format(title=SITE["title"], css=CSS, body=index_body())
    (ROOT / "index.html").write_text(index_html, encoding="utf-8")
    print("wrote index.html")
    print("빌드·검증 완료.")


if __name__ == "__main__":
    main()
