#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONEROOMCOOK 레시피 페이지 빌드 스크립트
=======================================
data/recipes.json 을 읽어 다음을 생성합니다.
  1. recipes/<slug>.html   — 레시피 상세 페이지 (Recipe JSON-LD 포함)
  2. recipes/index.html    — 레시피 아카이브 (카테고리 필터)
  3. assets/img/recipe-<slug>.svg — 브랜드 톤 일러스트 (실사진 교체 전 플레이스홀더)
  4. assets/img/ig-1..6.svg       — 인스타 피드 플레이스홀더

새 레시피 추가 방법 (운영자/인수자용):
  1. data/recipes.json 에 항목 추가 (기존 항목 복사 후 수정)
  2. python3 scripts/build.py 실행
  3. sitemap.xml 에 새 URL 한 줄 추가
  4. 실제 요리 사진이 있으면 assets/img/recipe-<slug>.jpg 로 저장하고
     recipes.json 의 "photo": true 로 두면 svg 대신 jpg 를 사용합니다.
"""
import json, html, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://jrkwak.github.io/oneroomcook"   # ★ 커스텀 도메인 적용 시 교체
TODAY = "2026-07-09"

with open(os.path.join(ROOT, "data", "recipes.json"), encoding="utf-8") as f:
    RECIPES = json.load(f)

PALETTES = [
    {"bg": "#F3E7D3", "main": "#C05A3A", "sub": "#D9A13F", "acc": "#7C8B6C"},
    {"bg": "#EFE3D8", "main": "#9A4326", "sub": "#C05A3A", "acc": "#D9A13F"},
    {"bg": "#F5EDDA", "main": "#D9A13F", "sub": "#C05A3A", "acc": "#7C8B6C"},
    {"bg": "#EEE6D6", "main": "#B98A4A", "sub": "#9A4326", "acc": "#7C8B6C"},
    {"bg": "#F2E9DC", "main": "#C0703A", "sub": "#7C8B6C", "acc": "#D9A13F"},
    {"bg": "#F0E2D2", "main": "#B44B31", "sub": "#D9A13F", "acc": "#7C8B6C"},
    {"bg": "#F4EBDB", "main": "#8F6B3E", "sub": "#C05A3A", "acc": "#7C8B6C"},
    {"bg": "#F1E8D9", "main": "#7C8B6C", "sub": "#D9A13F", "acc": "#C05A3A"},
]

STEAM = ('<path d="M{x1} {y}c-8 -12 8 -18 0 -32M{x2} {y}c-8 -12 8 -18 0 -32" '
         'fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round" opacity=".75"/>')

def dish_svg(kind, p):
    """접시/그릇 유형별 심플 일러스트."""
    if kind == "bowl":
        art = (f'<ellipse cx="200" cy="170" rx="95" ry="26" fill="{p["main"]}"/>'
               f'<path d="M105 170h190c0 42-38 66-95 66s-95-24-95-66z" fill="{p["main"]}"/>'
               f'<ellipse cx="200" cy="168" rx="80" ry="18" fill="{p["sub"]}"/>'
               f'<circle cx="185" cy="163" r="10" fill="#FFFDF8"/>'
               f'<circle cx="218" cy="167" r="7" fill="{p["acc"]}"/>'
               + STEAM.format(x1=185, x2=215, y=128, c=p["acc"]))
    elif kind == "pan":
        art = (f'<ellipse cx="185" cy="180" rx="105" ry="34" fill="#3A312B"/>'
               f'<ellipse cx="185" cy="172" rx="92" ry="26" fill="{p["main"]}"/>'
               f'<rect x="285" y="166" width="80" height="12" rx="6" fill="#3A312B"/>'
               f'<circle cx="160" cy="168" r="9" fill="{p["sub"]}"/>'
               f'<circle cx="200" cy="175" r="8" fill="{p["acc"]}"/>'
               f'<circle cx="222" cy="164" r="7" fill="#FFFDF8"/>'
               + STEAM.format(x1=165, x2=205, y=126, c=p["acc"]))
    elif kind == "plate":
        art = (f'<ellipse cx="200" cy="185" rx="120" ry="34" fill="#FFFDF8" stroke="{p["main"]}" stroke-width="5"/>'
               f'<path d="M140 178c20-22 44-30 62-24s26 20 52 16" fill="none" stroke="{p["sub"]}" stroke-width="14" stroke-linecap="round"/>'
               f'<circle cx="150" cy="170" r="7" fill="{p["acc"]}"/>'
               f'<circle cx="252" cy="172" r="6" fill="{p["acc"]}"/>'
               + STEAM.format(x1=185, x2=215, y=138, c=p["acc"]))
    elif kind == "cake":
        art = (f'<rect x="130" y="140" width="140" height="72" rx="12" fill="{p["main"]}"/>'
               f'<rect x="130" y="128" width="140" height="30" rx="12" fill="#4A3A2E"/>'
               f'<ellipse cx="200" cy="216" rx="110" ry="18" fill="#FFFDF8" stroke="{p["sub"]}" stroke-width="4"/>'
               f'<circle cx="200" cy="116" r="8" fill="{p["acc"]}"/>')
    elif kind == "pot":
        art = (f'<path d="M120 150h160v46a20 20 0 0 1-20 20H140a20 20 0 0 1-20-20z" fill="{p["main"]}"/>'
               f'<rect x="106" y="138" width="188" height="16" rx="8" fill="{p["sub"]}"/>'
               f'<rect x="80" y="152" width="30" height="10" rx="5" fill="{p["sub"]}"/>'
               f'<rect x="290" y="152" width="30" height="10" rx="5" fill="{p["sub"]}"/>'
               f'<ellipse cx="200" cy="150" rx="70" ry="10" fill="{p["acc"]}" opacity=".7"/>'
               + STEAM.format(x1=180, x2=220, y=118, c=p["acc"]))
    elif kind == "box":
        art = (f'<rect x="110" y="140" width="180" height="80" rx="10" fill="#FFFDF8" stroke="{p["main"]}" stroke-width="5"/>'
               f'<line x1="200" y1="145" x2="200" y2="215" stroke="{p["main"]}" stroke-width="4"/>'
               f'<rect x="124" y="156" width="60" height="48" rx="6" fill="{p["sub"]}"/>'
               f'<circle cx="245" cy="168" r="12" fill="{p["acc"]}"/>'
               f'<circle cx="264" cy="192" r="9" fill="{p["main"]}"/>'
               f'<rect x="110" y="126" width="180" height="16" rx="8" fill="{p["main"]}"/>')
    else:  # cup
        art = (f'<path d="M150 120h100v88a22 22 0 0 1-22 22h-56a22 22 0 0 1-22-22z" fill="#FFFDF8" stroke="{p["main"]}" stroke-width="5"/>'
               f'<path d="M154 168h92v40a18 18 0 0 1-18 18h-56a18 18 0 0 1-18-18z" fill="{p["sub"]}"/>'
               f'<circle cx="176" cy="150" r="8" fill="{p["acc"]}"/>'
               f'<circle cx="206" cy="144" r="6" fill="{p["main"]}"/>'
               f'<circle cx="224" cy="154" r="7" fill="{p["acc"]}"/>')
    return art

def recipe_svg(r):
    p = PALETTES[r["palette"] % len(PALETTES)]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" role="img" aria-label="{html.escape(r["title"])} 일러스트">
  <rect width="400" height="300" fill="{p["bg"]}"/>
  <circle cx="352" cy="46" r="60" fill="{p["sub"]}" opacity=".18"/>
  <circle cx="40" cy="262" r="70" fill="{p["main"]}" opacity=".12"/>
  <g transform="translate(0,14)">{dish_svg(r["dish"], p)}</g>
  <rect x="20" y="252" width="86" height="26" rx="13" fill="{p["main"]}"/>
  <text x="63" y="270" font-family="sans-serif" font-size="13" font-weight="700" fill="#FFFDF8" text-anchor="middle">{html.escape(r["categories"][0])}</text>
</svg>
'''

def head(title, desc, path, extra_ld=""):
    url = f"{BASE_URL}/{path}"
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="원룸쿡 ONEROOMCOOK">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{url}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
  <link rel="stylesheet" href="../assets/css/style.css">
{extra_ld}</head>
'''

def header_nav(active):
    def cur(k): return ' aria-current="page"' if k == active else ''
    return f'''<body>
  <a class="skip-link" href="#main">본문 바로가기</a>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="../index.html">
        <img src="../assets/img/logo-mark.svg" alt="" width="34" height="34">
        <span class="brand-name">원룸<em>쿡</em></span>
      </a>
      <button class="nav-toggle" aria-expanded="false" aria-label="메뉴 열기"><span></span><span></span><span></span></button>
      <nav class="nav" aria-label="주 메뉴">
        <a href="../index.html">홈</a>
        <a href="index.html"{cur("recipes")}>레시피</a>
        <a href="../about.html">스토리</a>
        <a href="../partnership.html">파트너십</a>
        <a class="btn" href="../contact.html">협업 문의</a>
      </nav>
    </div>
  </header>
'''

FOOTER = '''  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div>
          <a class="brand" href="../index.html" style="margin-bottom:1rem;">
            <img src="../assets/img/logo-mark.svg" alt="" width="30" height="30">
            <span class="brand-name">원룸<em>쿡</em></span>
          </a>
          <p class="small" style="max-width:26em;">좁은 원룸, 최소한의 장비로 차린 근사한 한 끼. 1인 가구의 식탁을 바꾸는 레시피 미디어.</p>
        </div>
        <div>
          <h4>Menu</h4>
          <ul>
            <li><a href="index.html">레시피 아카이브</a></li>
            <li><a href="../about.html">스토리</a></li>
            <li><a href="../partnership.html">파트너십 · 미디어킷</a></li>
            <li><a href="../contact.html">협업 문의</a></li>
          </ul>
        </div>
        <div>
          <h4>Contact</h4>
          <ul>
            <li><a href="https://www.instagram.com/oneroomcook/" target="_blank" rel="noopener">Instagram @oneroomcook</a></li>
            <li><a href="mailto:oneroomcook@gmail.com">oneroomcook@gmail.com</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© 2026 ONEROOMCOOK. All rights reserved.</span>
        <span>여섯 평에서도, 근사하게.</span>
      </div>
    </div>
  </footer>
  <script src="../assets/js/main.js" defer></script>
</body>
</html>
'''

def recipe_ld(r):
    img = f"{BASE_URL}/assets/img/recipe-{r['slug']}.svg"
    ld = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": r["title"],
        "description": r["subtitle"],
        "image": [img],
        "author": {"@type": "Organization", "name": "원룸쿡 ONEROOMCOOK", "url": BASE_URL + "/"},
        "datePublished": TODAY,
        "prepTime": r["prep_iso"],
        "cookTime": r["cook_iso"],
        "totalTime": r["total_iso"],
        "recipeYield": r["servings"],
        "recipeCategory": r["category_label"],
        "recipeCuisine": "Korean" if "한식" in r["categories"] else "International",
        "keywords": r["keywords"],
        "recipeIngredient": [f'{i["name"]} {i["amount"]}' for i in r["ingredients"]],
        "recipeInstructions": [
            {"@type": "HowToStep", "name": s["title"], "text": s["text"],
             "url": f"{BASE_URL}/recipes/{r['slug']}.html#step-{n+1}"}
            for n, s in enumerate(r["steps"])
        ],
        "tool": [{"@type": "HowToTool", "name": t} for t in r["equipment"]],
    }
    return ('  <script type="application/ld+json">\n  '
            + json.dumps(ld, ensure_ascii=False, indent=2).replace("\n", "\n  ")
            + "\n  </script>\n")

def build_recipe_page(r, prev_r, next_r):
    title = f'{r["title"]} — 원룸쿡 레시피'
    facts = f'''<dl class="recipe-facts">
          <div><dt>조리 시간</dt><dd>{r["time_display"]}</dd></div>
          <div><dt>난이도</dt><dd>{r["difficulty"]}</dd></div>
          <div><dt>분량</dt><dd>{r["servings"]}</dd></div>
          <div><dt>필요 화구</dt><dd>{html.escape(r["equipment"][0])}</dd></div>
        </dl>'''
    ing = "\n".join(
        f'            <li><b>{html.escape(i["name"])}</b><span>{html.escape(i["amount"])}</span></li>'
        for i in r["ingredients"])
    equip = " · ".join(html.escape(t) for t in r["equipment"])
    steps = "\n".join(
        f'            <li id="step-{n+1}"><b>{html.escape(s["title"])}</b>{html.escape(s["text"])}</li>'
        for n, s in enumerate(r["steps"]))
    nav_prev = (f'<a class="text-link" href="{prev_r["slug"]}.html">← {html.escape(prev_r["title"])}</a>'
                if prev_r else "<span></span>")
    nav_next = (f'<a class="text-link" href="{next_r["slug"]}.html">{html.escape(next_r["title"])} →</a>'
                if next_r else "<span></span>")

    return (head(title, r["subtitle"], f'recipes/{r["slug"]}.html', recipe_ld(r))
            + header_nav("recipes")
            + f'''  <main id="main">
    <div class="container recipe-hero">
      <p class="breadcrumb"><a href="../index.html">홈</a> / <a href="index.html">레시피</a> / {html.escape(r["categories"][0])}</p>
      <p class="kicker">{html.escape(r["category_label"])} · {r["time_display"]} · 난이도 {r["difficulty"]}</p>
      <h1>{html.escape(r["title"])}</h1>
      <p class="lede">{html.escape(r["subtitle"])}</p>
      <img src="../assets/img/recipe-{r["slug"]}.svg" alt="{html.escape(r["title"])} 완성 이미지" width="800" height="600" fetchpriority="high">
      {facts}
      <div class="recipe-layout">
        <aside class="ingredients">
          <h2>재료 <span class="muted small">({r["servings"]})</span></h2>
          <ul>
{ing}
          </ul>
          <div class="equip-note"><b>원룸 최소 장비</b><br>{equip}</div>
        </aside>
        <div>
          <h2 class="serif">만드는 법</h2>
          <ol class="steps">
{steps}
          </ol>
          <div class="recipe-tip"><b>원룸쿡의 한 끗</b><br>{html.escape(r["tip"])}</div>
        </div>
      </div>
      <nav class="recipe-nav" aria-label="레시피 이동">{nav_prev}{nav_next}</nav>
    </div>
  </main>
''' + FOOTER)

def build_archive():
    cats = ["전체", "한식", "양식", "야식", "밀프렙"]
    btns = "\n".join(
        f'          <button class="filter-btn{" active" if c == "전체" else ""}" data-filter="{"all" if c == "전체" else c}" aria-pressed="{"true" if c == "전체" else "false"}">{c}</button>'
        for c in cats)
    cards = ""
    for r in RECIPES:
        cats_attr = " ".join(r["categories"])
        cards += f'''          <a class="card recipe-card reveal" href="{r["slug"]}.html" data-categories="{cats_attr}">
            <div class="card-media"><img src="../assets/img/recipe-{r["slug"]}.svg" alt="{html.escape(r["title"])} 일러스트" loading="lazy" width="400" height="300"></div>
            <div class="card-body">
              <span class="card-tag">{html.escape(r["category_label"])}</span>
              <h3>{html.escape(r["title"])}</h3>
              <p class="muted small">{html.escape(r["subtitle"])}</p>
              <div class="card-meta"><span>⏱ {r["time_display"]}</span><span>난이도 {r["difficulty"]}</span><span>{html.escape(r["equipment"][0])}</span></div>
            </div>
          </a>
'''
    desc = "1구 인덕션과 60cm 조리대에서 완성한 원룸쿡의 전체 레시피. 한식·양식·야식·밀프렙 카테고리별로 골라보세요."
    ld = ('  <script type="application/ld+json">\n  '
          + json.dumps({
              "@context": "https://schema.org", "@type": "CollectionPage",
              "name": "원룸쿡 레시피 아카이브", "url": f"{BASE_URL}/recipes/index.html",
              "description": desc, "inLanguage": "ko"}, ensure_ascii=False, indent=2).replace("\n", "\n  ")
          + "\n  </script>\n")
    return (head("레시피 아카이브 — 원룸쿡", desc, "recipes/index.html", ld)
            + header_nav("recipes")
            + f'''  <main id="main">
    <section>
      <div class="container">
        <div class="section-head">
          <p class="kicker">Recipe Archive</p>
          <h1 style="font-size:var(--fs-h2);">레시피 아카이브</h1>
          <p class="muted">모든 레시피는 1구 인덕션 · 조리대 60cm · 미니 오븐, 세 가지 제약 안에서 완성되었습니다. 장비 걱정 없이 골라 만드세요.</p>
        </div>
        <div class="filter-bar" role="group" aria-label="카테고리 필터">
{btns}
        </div>
        <p class="archive-count">총 <b>{len(RECIPES)}</b>개의 레시피</p>
        <div class="grid-3">
{cards}        </div>
      </div>
    </section>
  </main>
''' + FOOTER)

def ig_placeholder(i):
    p = PALETTES[(i * 3) % len(PALETTES)]
    kinds = ["bowl", "pan", "plate", "pot", "cup", "box"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" role="img" aria-label="인스타그램 게시물 플레이스홀더 {i}">
  <rect width="300" height="300" fill="{p["bg"]}"/>
  <g transform="translate(-50,30) scale(.75)">{dish_svg(kinds[(i-1) % 6], p)}</g>
  <circle cx="258" cy="42" r="18" fill="none" stroke="{p["main"]}" stroke-width="4"/>
  <circle cx="258" cy="42" r="7" fill="{p["main"]}"/>
</svg>
'''

# ---- 실행 ------------------------------------------------------------------
os.makedirs(os.path.join(ROOT, "recipes"), exist_ok=True)
for idx, r in enumerate(RECIPES):
    prev_r = RECIPES[idx - 1] if idx > 0 else None
    next_r = RECIPES[idx + 1] if idx < len(RECIPES) - 1 else None
    with open(os.path.join(ROOT, "recipes", r["slug"] + ".html"), "w", encoding="utf-8") as f:
        f.write(build_recipe_page(r, prev_r, next_r))
    with open(os.path.join(ROOT, "assets", "img", f"recipe-{r['slug']}.svg"), "w", encoding="utf-8") as f:
        f.write(recipe_svg(r))

with open(os.path.join(ROOT, "recipes", "index.html"), "w", encoding="utf-8") as f:
    f.write(build_archive())

for i in range(1, 7):
    with open(os.path.join(ROOT, "assets", "img", f"ig-{i}.svg"), "w", encoding="utf-8") as f:
        f.write(ig_placeholder(i))

print(f"✓ {len(RECIPES)} recipe pages, archive, {len(RECIPES)} recipe SVGs, 6 IG placeholders generated.")
