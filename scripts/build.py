#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONEROOMCOOK 레시피 페이지 빌드 스크립트 (v3 — site.css 다크 테마, 네이버 블로그 레시피)
data/recipes.json → recipes/<slug>.html + recipes/index.html + sitemap.xml 생성.

새 레시피 추가
  1. 사진 2장을 assets/img/recipes/ 에 넣음 (완성 사진 <slug>.jpg, 레시피 카드 <slug>-card.jpg)
  2. data/recipes.json 에 항목 추가 (블로그 본문의 재료·만드는 법·원룸 팁·마무리)
  3. python3 scripts/build.py
홈(index.html)의 Signature·Tasting Course 는 수동 관리.
"""
import json, html, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://jrkwak.github.io/oneroomcook"
TODAY = "2026-11-09"
CSS_V = "3"
E = html.escape

with open(os.path.join(ROOT, "data", "recipes.json"), encoding="utf-8") as f:
    RECIPES = json.load(f)

ARCHIVE_DESC = "원룸쿡 네이버 블로그에 올린 레시피 모음. 1구 인덕션과 프라이팬 하나로 완성하는 한 접시."


def img_url(name):
    return f"{BASE_URL}/assets/img/recipes/{name}"


def head(title, desc, path, og_type, og_image, ld):
    url = f"{BASE_URL}/{path}"
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{E(title)}</title>
  <meta name="description" content="{E(desc)}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="원룸쿡 ONEROOMCOOK">
  <meta property="og:title" content="{E(title)}">
  <meta property="og:description" content="{E(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#0B0A09">
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Noto+Serif+KR:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
  <link rel="stylesheet" href="../assets/css/site.css?v={CSS_V}">
  <script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
  </script>
</head>
<body>
  <a class="skip-link" href="#main">본문 바로가기</a>
  <header class="site-header">
    <a class="logo" href="../index.html">ONEROOMCOOK</a>
    <nav class="main-nav" aria-label="주 메뉴">
      <a href="../recipes/index.html" aria-current="page">Recipes</a>
      <a href="../about.html">Story</a>
      <a href="../contact.html">Contact Us</a>
    </nav>
    <button class="burger" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
  </header>
  <nav class="mobile-menu" aria-label="모바일 메뉴">
    <a href="../index.html">Home</a>
    <a href="../recipes/index.html" aria-current="page">Recipes</a>
    <a href="../about.html">Story</a>
    <a href="../contact.html">Contact Us</a>
  </nav>
'''


FOOTER = f'''  <footer class="site-footer">
    <div class="footer-grid">
      <div>
        <a class="logo" href="../index.html">ONEROOMCOOK</a>
        <p class="tagline">여섯 평에서도, 근사하게.</p>
      </div>
      <nav class="footer-nav" aria-label="푸터 메뉴">
        <a href="../recipes/index.html">Recipes</a>
        <a href="../about.html">Story</a>
        <a href="../contact.html">Contact Us</a>
      </nav>
    </div>
    <div class="footer-meta">
      <span>© 2026 ONEROOMCOOK · Photos: ONEROOMCOOK</span>
      <span>
        <a href="https://www.instagram.com/oneroomcook/" target="_blank" rel="noopener">Instagram</a>
        &nbsp;·&nbsp; <a href="https://blog.naver.com/oneroomcook" target="_blank" rel="noopener">Blog</a>
        &nbsp;·&nbsp; <a href="mailto:oneroomcook@gmail.com">oneroomcook@gmail.com</a>
      </span>
    </div>
  </footer>
  <script src="../assets/js/site.js?v={CSS_V}" defer></script>
</body>
</html>
'''


def recipe_page(i, r):
    path = f"recipes/{r['slug']}.html"
    url = f"{BASE_URL}/{path}"
    ld = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": r["title"],
        "description": r["subtitle"],
        "image": [img_url(r["photo"])] + ([img_url(r["card"])] if r.get("card") else []),
        "author": {"@type": "Organization", "name": "원룸쿡 ONEROOMCOOK", "url": f"{BASE_URL}/"},
        "datePublished": r.get("date", TODAY),
        "prepTime": r["prep_iso"], "cookTime": r["cook_iso"], "totalTime": r["total_iso"],
        "recipeYield": r["servings"],
        "recipeCategory": r["category_label"],
        "recipeCuisine": "Korean" if r["category_label"] != "양식" else "International",
        "keywords": r["keywords"],
        "recipeIngredient": [f"{x['name']} {x['amount']}" for x in r["ingredients"]],
        "recipeInstructions": [
            {"@type": "HowToStep", "name": s.get("title") or f"Step {n}", "text": s["text"], "url": f"{url}#step-{n}"}
            for n, s in enumerate(r["steps"], 1)
        ],
        "tool": [{"@type": "HowToTool", "name": t} for t in r["equipment"]],
    }
    out = [head(f"{r['title']} — 원룸쿡", r["subtitle"], path, "article", img_url(r["photo"]), ld)]
    ings = "\n".join(f"              <li>{E(x['name'])}<span>{E(x['amount'])}</span></li>" for x in r["ingredients"])
    steps = "\n".join(
        f'              <li id="step-{n}">' + (f'<b>{E(s["title"])}</b>' if s.get("title") else '') + f'<span>{E(s["text"])}</span></li>'
        for n, s in enumerate(r["steps"], 1))
    tips = "".join(f"<p>{E(t)}</p>" for t in r.get("tips", []))
    tips_html = f'<div class="rx-tip"><b>Chef\'s Note — 원룸 팁</b>{tips}</div>' if tips else ''
    closing_html = f'<p class="rx-closing">{E(r["closing"])}</p>' if r.get("closing") else ''
    card_html = (f'''<figure class="rx-card">
          <img src="../assets/img/recipes/{r['card']}" alt="{E(r.get('card_alt', r['title'] + ' 레시피 카드'))}" loading="lazy">
          <figcaption>{E(r.get('card_caption', 'Recipe Card — 한 장으로 보는 레시피'))}</figcaption>
        </figure>''' if r.get("card") else '')
    intro_html = f'<p class="rx-intro">{E(r["intro"])}</p>' if r.get("intro") else ''
    prev_r = RECIPES[i - 1] if i > 0 else None
    next_r = RECIPES[i + 1] if i < len(RECIPES) - 1 else None
    nav = (f'<a href="{prev_r["slug"]}.html" rel="prev">← {E(prev_r["short"])}</a>' if prev_r else '<span></span>') + \
          (f'<a href="{next_r["slug"]}.html" rel="next">{E(next_r["short"])} →</a>' if next_r else '<a href="index.html">전체 레시피 →</a>')
    out.append(f'''  <main id="main">
    <div class="page-hero">
      <p class="breadcrumb"><a href="../index.html">Home</a> / <a href="index.html">Recipes</a> / {E(r['category_label'])}</p>
      <p class="label">{E(r['category_label'])} · {E(r['time_display'])} · 난이도 {E(r['difficulty'])}</p>
      <h1>{E(r['title'])}</h1>
      <p class="lede">{E(r['subtitle'])}</p>
    </div>
    <div class="section tight">
      <div class="container">
        <img class="rx-hero-img square" src="../assets/img/recipes/{r['photo']}" alt="{E(r['photo_alt'])}" fetchpriority="high">
        <dl class="rx-facts">
          <div><dt>Time</dt><dd>{E(r['time_display'])}</dd></div>
          <div><dt>Difficulty</dt><dd>{E(r['difficulty'])}</dd></div>
          <div><dt>Serves</dt><dd>{E(r['servings'])}</dd></div>
          <div><dt>Equipment</dt><dd>{E(r['equipment'][0])}</dd></div>
        </dl>
        {intro_html}
        <div class="rx-layout">
          <aside class="rx-ing">
            <h2>Ingredients <small>({E(r['servings'])})</small></h2>
            <ul>
{ings}
            </ul>
            <div class="rx-equip"><b>ONE-ROOM SETUP</b>{E(' · '.join(r['equipment']))}</div>
          </aside>
          <div>
            <h2 class="rx-method-title">Méthode</h2>
            <ol class="rx-steps">
{steps}
            </ol>
            {tips_html}
            {closing_html}
          </div>
        </div>
        {card_html}
        <nav class="rx-nav" aria-label="레시피 이동">{nav}</nav>
      </div>
    </div>
  </main>
''')
    out.append(FOOTER)
    return "".join(out)


def archive_page():
    cats = []
    for r in RECIPES:
        for c in r["categories"]:
            if c not in cats:
                cats.append(c)
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "원룸쿡 레시피 아카이브",
          "url": f"{BASE_URL}/recipes/index.html", "description": ARCHIVE_DESC, "inLanguage": "ko"}
    out = [head("Full Menu — 원룸쿡 레시피 아카이브", ARCHIVE_DESC, "recipes/index.html", "website",
                img_url(RECIPES[0]["photo"]), ld)]
    btns = "\n".join(f'          <button data-filter="{E(c)}" aria-pressed="false">{E(c)}</button>' for c in cats)
    cards = "\n".join(f'''          <a class="dish-card" href="{r['slug']}.html" data-categories="{E(' '.join(r['categories']))}">
            <div class="dc-media"><img src="../assets/img/recipes/{r['photo']}" alt="{E(r['photo_alt'])}" loading="lazy"></div>
            <div class="dc-body">
              <span class="dc-tag">{E(r['category_label'])}</span>
              <h3>{E(r['title'])}</h3>
              <p>{E(r['subtitle'])}</p>
              <div class="dc-meta"><span>⏱ {E(r['time_display'])}</span><span>난이도 {E(r['difficulty'])}</span><span>{E(r['equipment'][0])}</span></div>
            </div>
          </a>''' for r in RECIPES)
    out.append(f'''  <main id="main">
    <div class="page-hero">
      <p class="label">Full Menu</p>
      <h1>레시피 <span class="gold">아카이브</span></h1>
      <p class="lede">모든 접시는 1구 인덕션 · 조리대 60cm · 미니 오븐, 세 가지 제약 안에서 완성되었습니다.</p>
    </div>
    <div class="section tight">
      <div class="container">
        <div class="filter-bar" role="group" aria-label="카테고리 필터">
          <button class="active" data-filter="all" aria-pressed="true">전체</button>
{btns}
        </div>
        <p class="archive-count">Nº of dishes — <b>{len(RECIPES)}</b></p>
        <div class="dish-grid">
{cards}
        </div>
      </div>
    </div>
  </main>
''')
    out.append(FOOTER)
    return "".join(out)


def sitemap():
    pages = ["", "recipes/index.html"] + [f"recipes/{r['slug']}.html" for r in RECIPES] + \
            ["about.html", "contact.html"]
    rows = "\n".join(f"  <url><loc>{BASE_URL}/{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in pages)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}\n</urlset>\n'


def write(rel, text):
    with open(os.path.join(ROOT, rel), "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote", rel)


if __name__ == "__main__":
    keep = {f"{r['slug']}.html" for r in RECIPES} | {"index.html"}
    for p in glob.glob(os.path.join(ROOT, "recipes", "*.html")):
        if os.path.basename(p) not in keep:
            os.remove(p)
            print("removed", os.path.relpath(p, ROOT))
    for i, r in enumerate(RECIPES):
        write(f"recipes/{r['slug']}.html", recipe_page(i, r))
    write("recipes/index.html", archive_page())
    write("sitemap.xml", sitemap())
