#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONEROOMCOOK 레시피 페이지 빌드 스크립트 (v4 — LUXE 다크 테마)
data/recipes.json → recipes/<slug>.html + recipes/index.html 생성.
새 레시피 추가: recipes.json에 항목 추가 → python3 scripts/build.py → sitemap에 URL 1줄.
사진 교체: 아래 PHOTOS의 URL을 실제 요리 사진으로 바꾸면 끝. (현재: Unsplash 라이선스 무료 실사)
"""
import json, html, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://jrkwak.github.io/oneroomcook"
TODAY = "2026-07-09"
U = "https://images.unsplash.com/"
PHOTOS = {
    "butter-soy-egg-rice":       U+"photo-1550807014-1236e91b92d4",
    "one-pan-kimchi-jeyuk":      U+"photo-1625604086816-4bfaf603e842",
    "one-pan-cream-pasta":       U+"photo-1612929633738-8fe44f7ec841",
    "mini-oven-basque":          U+"photo-1458253756247-1e4ed949191b",
    "microwave-egg-jjim":        U+"photo-1587497539328-7e140d2ec8d1",
    "gukmul-tteokbokki":         U+"photo-1553025934-296397db4010",
    "chicken-teriyaki-mealprep": U+"photo-1761416376088-d6456fcd76fd",
    "overnight-oats":            U+"photo-1590064293071-c2610e23d86f",
}
def photo(slug, w=1600, extra=""):
    return f"{PHOTOS[slug]}?auto=format&fit=crop&w={w}&q=70{extra}"

with open(os.path.join(ROOT, "data", "recipes.json"), encoding="utf-8") as f:
    RECIPES = json.load(f)

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
  <meta name="theme-color" content="#0B0A09">
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://images.unsplash.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Noto+Serif+KR:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
  <link rel="stylesheet" href="../assets/css/luxe.css">
{extra_ld}</head>
'''

def header_nav():
    return '''<body class="luxe">
  <div class="grain" aria-hidden="true"></div>
  <div class="cursor-dot" aria-hidden="true"></div>
  <div class="cursor-ring" aria-hidden="true"></div>
  <header class="lx-header solid">
    <a class="lx-logo" href="../index.html">ONEROOMCOOK</a>
    <nav class="lx-nav" aria-label="주 메뉴">
      <a href="index.html">Recipes</a>
      <a href="../about.html">Story</a>
      <a href="../partnership.html">Partnership</a>
      <a href="../contact.html">Contact</a>
    </nav>
    <button class="lx-burger" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
  </header>
  <div class="lx-menu" aria-label="모바일 메뉴">
    <a href="../index.html">Home</a>
    <a href="index.html">Recipes</a>
    <a href="../about.html">Story</a>
    <a href="../partnership.html">Partnership</a>
    <a href="../contact.html">Contact</a>
  </div>
'''

FOOTER = '''  <footer class="lx-footer">
    <span class="lx-logo">ONEROOMCOOK</span>
    <span>여섯 평에서도, 근사하게.</span>
    <span>
      <a href="https://www.instagram.com/oneroomcook/" target="_blank" rel="noopener">Instagram</a>
      &nbsp;·&nbsp; <a href="mailto:oneroomcook@gmail.com">Email</a>
      &nbsp;·&nbsp; © 2026 &nbsp;·&nbsp; <span style="opacity:.6">Photos: Unsplash</span>
    </span>
  </footer>
  <script src="../assets/js/luxe.js" defer></script>
</body>
</html>
'''

def recipe_ld(r):
    ld = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": r["title"],
        "description": r["subtitle"],
        "image": [photo(r["slug"], 1200)],
        "author": {"@type": "Organization", "name": "원룸쿡 ONEROOMCOOK", "url": BASE_URL + "/"},
        "datePublished": TODAY,
        "prepTime": r["prep_iso"], "cookTime": r["cook_iso"], "totalTime": r["total_iso"],
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
    title = f'{r["title"]} — 원룸쿡'
    ing = "\n".join(
        f'              <li>{html.escape(i["name"])}<span>{html.escape(i["amount"])}</span></li>'
        for i in r["ingredients"])
    equip = " · ".join(html.escape(t) for t in r["equipment"])
    steps = "\n".join(
        f'              <li id="step-{n+1}"><b>{html.escape(s["title"])}</b><span>{html.escape(s["text"])}</span></li>'
        for n, s in enumerate(r["steps"]))
    nav_prev = (f'<a href="{prev_r["slug"]}.html">← {html.escape(prev_r["title"])}</a>' if prev_r else "<span></span>")
    nav_next = (f'<a href="{next_r["slug"]}.html">{html.escape(next_r["title"])} →</a>' if next_r else "<span></span>")
    return (head(title, r["subtitle"], f'recipes/{r["slug"]}.html', recipe_ld(r))
            + header_nav()
            + f'''  <main>
    <div class="lx-page-hero">
      <p class="lx-breadcrumb"><a href="../index.html">Home</a> / <a href="index.html">Recipes</a> / {html.escape(r["categories"][0])}</p>
      <p class="lx-label">{html.escape(r["category_label"])} · {r["time_display"]} · 난이도 {r["difficulty"]}</p>
      <h1>{html.escape(r["title"])}</h1>
      <p class="lx-p">{html.escape(r["subtitle"])}</p>
    </div>
    <div class="lx-section" style="padding-top:0;">
      <div class="lx-container">
        <img class="rx-hero-img" src="{photo(r["slug"], 1800)}" alt="{html.escape(r["title"])} — 다크 무드 요리 사진" fetchpriority="high">
        <dl class="rx-facts">
          <div><dt>Time</dt><dd>{r["time_display"]}</dd></div>
          <div><dt>Difficulty</dt><dd>{r["difficulty"]}</dd></div>
          <div><dt>Serves</dt><dd>{r["servings"]}</dd></div>
          <div><dt>Equipment</dt><dd>{html.escape(r["equipment"][0])}</dd></div>
        </dl>
        <div class="rx-layout">
          <aside class="rx-ing">
            <h2>Ingredients <small class="lx-form-note">({r["servings"]})</small></h2>
            <ul>
{ing}
            </ul>
            <div class="rx-equip"><b>ONE-ROOM SETUP</b>{equip}</div>
          </aside>
          <div>
            <h2 class="lx-h2" style="font-size:clamp(1.5rem,3vw,2.1rem);">Méthode</h2>
            <ol class="rx-steps">
{steps}
            </ol>
            <div class="rx-tip"><b>Chef's Note — 원룸쿡의 한 끗</b><p>{html.escape(r["tip"])}</p></div>
          </div>
        </div>
        <nav class="rx-nav" aria-label="레시피 이동">{nav_prev}{nav_next}</nav>
      </div>
    </div>
  </main>
''' + FOOTER)

def build_archive():
    cats = ["전체", "한식", "양식", "야식", "밀프렙"]
    btns = "\n".join(
        f'          <button class="{"active" if c == "전체" else ""}" data-filter="{"all" if c == "전체" else c}" aria-pressed="{"true" if c == "전체" else "false"}">{c}</button>'
        for c in cats)
    cards = ""
    for r in RECIPES:
        cats_attr = " ".join(r["categories"])
        cards += f'''          <a class="dish-card recipe-card lx-reveal" href="{r["slug"]}.html" data-categories="{cats_attr}">
            <div class="dc-media"><img src="{photo(r["slug"], 900)}" alt="{html.escape(r["title"])} 다크 무드 사진" loading="lazy" width="900" height="675"></div>
            <div class="dc-body">
              <span class="dc-tag">{html.escape(r["category_label"])}</span>
              <h3>{html.escape(r["title"])}</h3>
              <p>{html.escape(r["subtitle"])}</p>
              <div class="dc-meta"><span>⏱ {r["time_display"]}</span><span>난이도 {r["difficulty"]}</span><span>{html.escape(r["equipment"][0])}</span></div>
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
    return (head("Full Menu — 원룸쿡 레시피 아카이브", desc, "recipes/index.html", ld)
            + header_nav()
            + f'''  <main>
    <div class="lx-page-hero">
      <p class="lx-label">Full Menu</p>
      <h1>레시피 <span class="gold">아카이브</span></h1>
      <p class="lx-p">모든 접시는 1구 인덕션 · 조리대 60cm · 미니 오븐, 세 가지 제약 안에서 완성되었습니다.</p>
    </div>
    <div class="lx-section" style="padding-top:0;">
      <div class="lx-container">
        <div class="lx-filter filter-bar" role="group" aria-label="카테고리 필터">
{btns}
        </div>
        <p class="lx-count archive-count">Nº of dishes — <b>{len(RECIPES)}</b></p>
        <div class="dish-grid">
{cards}        </div>
      </div>
    </div>
  </main>
''' + FOOTER)

os.makedirs(os.path.join(ROOT, "recipes"), exist_ok=True)
for idx, r in enumerate(RECIPES):
    prev_r = RECIPES[idx - 1] if idx > 0 else None
    next_r = RECIPES[idx + 1] if idx < len(RECIPES) - 1 else None
    with open(os.path.join(ROOT, "recipes", r["slug"] + ".html"), "w", encoding="utf-8") as f:
        f.write(build_recipe_page(r, prev_r, next_r))
with open(os.path.join(ROOT, "recipes", "index.html"), "w", encoding="utf-8") as f:
    f.write(build_archive())
print(f"✓ LUXE: {len(RECIPES)} recipe pages + archive rebuilt")
