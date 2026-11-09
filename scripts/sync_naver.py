#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 블로그(oneroomcook) → data/recipes.json 동기화.

동작
  1. RSS(rss.blog.naver.com/oneroomcook.xml)에서 최근 글 목록을 읽음
  2. 글마다 본문을 가져와 '재료'와 '만드는 법' 섹션이 있는 글만 레시피로 인식
  3. 새 글  → recipes.json 맨 앞에 추가하고 사진을 assets/img/recipes/ 에 저장
     수정된 글 → 본문(인트로·재료·만드는 법·원룸 팁·마무리)만 갱신
                 (직접 다듬은 부제·사진·조리시간·난이도·도구는 유지)
  4. 변경이 있으면 종료 코드 0과 함께 "CHANGED" 출력 → 워크플로가 build.py 실행 후 커밋

글 형식(블로그 본문 순서)
  인트로 문단 → '재료 (N인분)' → 재료 줄 → '만드는 법' → 단계 → '원룸 팁' → 팁 → '마무리' → 문단 → #해시태그
  "AI 활용" 표시된 이미지를 대표 이미지로, 직접 찍은 사진은 페이지 하단에 사용 (AI 이미지가 없으면 첫 사진이 대표).

실행
  python3 scripts/sync_naver.py            # 동기화
  python3 scripts/sync_naver.py --html FILE --logno N   # 저장된 HTML로 파서만 테스트 (네트워크 없음)
"""
import argparse, hashlib, html, io, json, os, re, sys, time
import urllib.request
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "recipes.json")
IMG_DIR = os.path.join(ROOT, "assets", "img", "recipes")
BLOG_ID = "oneroomcook"
RSS_URL = f"https://rss.blog.naver.com/{BLOG_ID}.xml"
POST_URL = "https://blog.naver.com/PostView.naver?blogId={blog}&logNo={no}&redirect=Dlog&widgetTypeCall=true&directAccess=false"
UA = "Mozilla/5.0 (compatible; oneroomcook-site-sync/1.0; +https://jrkwak.github.io/oneroomcook/)"

SECTION_RE = {
    "ingredients": re.compile(r"^재료\s*(\(([^)]*)\))?\s*$"),
    "steps": re.compile(r"^(만드는\s*법|조리\s*법|레시피)\s*$"),
    "tips": re.compile(r"^(원룸\s*팁|팁|TIP|Tip|꿀팁)\s*$"),
    "closing": re.compile(r"^(마무리|후기|정리)\s*$"),
}
NOISE = {"AI 활용", "AI 활용 설정", "대표사진 삭제", "사진 설명을 입력하세요.", "태그", "본문 기타 기능", "URL 복사", "통계"}
QTY = re.compile(r"\s(?=(\d|½|¼|한\s?(줌|공기|개|컵|큰술|작은술|쪽|대|장|팩|봉)|반\s?(개|컵|공기)|약간|몇\s|조금|적당량|취향껏))")


# ---------------------------------------------------------------- fetch
def get(url, referer=None, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **({"Referer": referer} if referer else {})})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                return data if binary else data.decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                raise
            print(f"  retry {url}: {e}", file=sys.stderr)
            time.sleep(3)


def rss_items():
    root = ET.fromstring(get(RSS_URL))
    items = []
    for it in root.iter("item"):
        link = (it.findtext("guid") or it.findtext("link") or "").strip()
        m = re.search(r"(\d{9,})", link)
        if not m:
            continue
        items.append({
            "logno": m.group(1),
            "title": html.unescape((it.findtext("title") or "").strip()),
            "date": (it.findtext("pubDate") or "").strip(),
        })
    return items


# ---------------------------------------------------------------- parse
def clean(t):
    t = t.replace("​", "").replace("\xa0", " ").replace("﻿", "")
    return re.sub(r"[ \t]+", " ", t).strip()


def blocks_from_html(doc):
    """SmartEditor ONE 본문 → [('text', line) | ('image', url)] 순서 목록."""
    soup = BeautifulSoup(doc, "html.parser")
    main = soup.select_one(".se-main-container") or soup.select_one("#postViewArea") or soup
    out = []
    comps = main.select(".se-component") or [main]
    for c in comps:
        cls = " ".join(c.get("class", []))
        if "se-image" in cls or "se-imageStrip" in cls or "se-imageGroup" in cls:
            is_ai = "AI 활용" in c.get_text(" ") or bool(c.select("[class*=ai], [class*=Ai], [class*=AI]"))
            for img in c.select("img"):
                u = img.get("data-lazy-src") or img.get("src") or ""
                if "pstatic" in u:
                    out.append(("ai_image" if is_ai else "image", u))
            continue
        if any(k in cls for k in ("se-oglink", "se-map", "se-placesMap", "se-video", "se-sticker", "se-horizontalLine", "se-documentTitle")):
            continue
        paras = c.select(".se-text-paragraph") or c.find_all(["p", "li"])
        for p in paras:
            t = clean(p.get_text(" "))
            if t:
                out.append(("text", t))
    return out


def split_ingredient_line(line):
    """'양파 1/4개, 마늘 2쪽' / '소스: 간장 2큰술, ...' → [{name, amount}, ...]"""
    line = re.sub(r"^[\-\*•·]\s*", "", line)
    prefix = ""
    m = re.match(r"^([^:：]{1,10})[:：]\s*(.+)$", line)
    if m:
        prefix, line = m.group(1).strip() + " — ", m.group(2)
    parts, depth, buf = [], 0, ""
    for ch in line:
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            parts.append(buf); buf = ""
        else:
            buf += ch
    parts.append(buf)
    res = []
    for part in (p.strip() for p in parts):
        if not part:
            continue
        m = QTY.search(part)
        name, amount = (part[:m.start()].strip(), part[m.end():].strip()) if m else (part, "")
        # '소금·후추 약간' 처럼 수량이 뒤에 붙는 경우 외에, '(약 90g)' 괄호만 있는 경우 처리
        if not amount:
            pm = re.match(r"^(.*?)\s*(\(.+\))$", part)
            if pm and re.search(r"\d", pm.group(2)):
                name, amount = pm.group(1), pm.group(2).strip("()")
        res.append({"name": prefix + name, "amount": amount})
    return res


def parse_post(doc, title_hint=""):
    blocks = blocks_from_html(doc)
    texts = [t for k, t in blocks if k == "text"]
    ai_images = [u for k, u in blocks if k == "ai_image"]
    real_images = [u for k, u in blocks if k == "image"]
    title = title_hint
    sec, servings = "intro", "1인분"
    buckets = {"intro": [], "ingredients": [], "steps": [], "tips": [], "closing": []}
    hashtags = []
    for t in texts:
        if t in NOISE or t == title:
            continue
        if t.startswith("#"):
            hashtags += re.findall(r"#(\S+)", t)
            continue
        hit = None
        for name, rx in SECTION_RE.items():
            m = rx.match(t)
            if m:
                hit = name
                if name == "ingredients" and m.group(2):
                    servings = m.group(2).strip()
                break
        if hit:
            sec = hit
            continue
        buckets[sec].append(t)
    if not buckets["ingredients"] or not buckets["steps"]:
        return None  # 레시피 글이 아님
    ings = []
    for line in buckets["ingredients"]:
        ings += split_ingredient_line(line)
    steps = [{"title": "", "text": re.sub(r"^\d+\s*[.)]\s*", "", s)} for s in buckets["steps"]]
    tips = [re.sub(r"^[\-\*•·]\s*", "", t) for t in buckets["tips"]]
    return {
        "intro": " ".join(buckets["intro"]),
        "servings": servings,
        "ingredients": ings,
        "steps": steps,
        "tips": tips,
        "closing": " ".join(buckets["closing"]),
        "hashtags": hashtags,
        # 대표 이미지는 AI 이미지 우선, 두 번째 이미지는 직접 찍은 사진 우선
        "images": (ai_images[:1] + real_images[:1] + ai_images[1:] + real_images[1:]) if ai_images
                  else real_images,
        "has_ai": bool(ai_images),
    }


# ---------------------------------------------------------------- derive
def norm_title(t):
    return re.sub(r"\s+", "", re.sub(r"\([^)]*\)", "", t))


def derive_meta(title, p):
    body = " ".join([title, p["intro"]] + [s["text"] for s in p["steps"]] + p["hashtags"])
    if re.search(r"덮밥|비빔밥|돈부리", title):
        cat = "덮밥"
    elif re.search(r"리조또|파스타|스테이크|샐러드|토스트|오믈렛|그라탕|브런치", body):
        cat = "양식"
    else:
        cat = "한식"
    mins = 0
    for s in p["steps"]:
        for m in re.finditer(r"(\d+)(?:\s*~\s*(\d+))?\s*분", s["text"]):
            mins += int(m.group(2) or m.group(1))
    total = max(10, int(round((mins + 5) / 5.0)) * 5)
    steps_txt = " ".join(s["text"] for s in p["steps"])
    equip = ["1구 인덕션"]
    if re.search(r"냄비|삶|끓", steps_txt): equip.append("냄비 1개")
    if re.search(r"팬", steps_txt): equip.append("프라이팬 1개")
    if re.search(r"오븐|에어프라이어", steps_txt): equip.append("미니 오븐")
    if not re.search(r"불|굽|볶|삶|끓|익히|졸", steps_txt):
        equip = ["불 없이"]
    short_src = re.sub(r"\([^)]*\)", "", title).strip()
    words = short_src.split()
    short = " ".join(words[-2:]) if len(words) > 2 else short_src
    first = re.split(r"(?<=[.!?요])\s", p["intro"])[0] if p["intro"] else short_src
    return {
        "categories": [cat], "category_label": cat,
        "time_display": f"{total}분", "prep_iso": "PT5M", "cook_iso": f"PT{max(total - 5, 0)}M", "total_iso": f"PT{total}M",
        "difficulty": "하" if len(p["steps"]) <= 5 else "중",
        "equipment": equip,
        "short": short,
        "subtitle": first[:120],
        "keywords": ", ".join(p["hashtags"]) or short,
    }


def save_image(url, dest_name):
    from PIL import Image
    u = re.sub(r"\?type=[^&]+", "", url) + "?type=w966"
    data = get(u, referer="https://blog.naver.com/", binary=True)
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if im.width > 1600:
        im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    im.save(os.path.join(IMG_DIR, dest_name), quality=82, optimize=True, progressive=True)
    return dest_name


def content_hash(p):
    keep = {k: p[k] for k in ("intro", "ingredients", "steps", "tips", "closing")}
    return hashlib.sha1(json.dumps(keep, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]


# ---------------------------------------------------------------- main
def sync():
    recipes = json.load(open(DATA, encoding="utf-8"))
    by_no = {r.get("naver_logno"): r for r in recipes if r.get("naver_logno")}
    by_title = {norm_title(r["title"]): r for r in recipes}
    changed = False
    items = rss_items()
    print(f"RSS: {len(items)} posts")
    new_entries = []
    for it in items:
        no = it["logno"]
        try:
            doc = get(POST_URL.format(blog=BLOG_ID, no=no))
        except Exception as e:  # noqa: BLE001
            print(f"  skip {no}: fetch failed ({e})")
            continue
        p = parse_post(doc, it["title"])
        if not p:
            print(f"  - {no} {it['title']} (레시피 형식 아님, 건너뜀)")
            continue
        h = content_hash(p)
        r = by_no.get(no) or by_title.get(norm_title(it["title"]))
        if r is not None:
            if not r.get("naver_logno"):
                r["naver_logno"] = no
                r["naver_hash"] = h
                changed = True
                print(f"  = {no} {it['title']} (기존 레시피와 연결)")
                continue
            if r.get("naver_hash") == h:
                continue
            old_titles = [s.get("title", "") for s in r.get("steps", [])]
            steps = p["steps"]
            if len(old_titles) == len(steps):
                for s, t in zip(steps, old_titles):
                    s["title"] = t
            r.update({k: p[k] for k in ("intro", "ingredients", "tips", "closing", "servings")})
            r["steps"] = steps
            r["naver_hash"] = h
            changed = True
            print(f"  ~ {no} {it['title']} (본문 수정 반영)")
            continue
        # 새 글
        slug = f"naver-{no}"
        if not p["images"]:
            print(f"  - {no} {it['title']} (사진 없음, 건너뜀)")
            continue
        try:
            photo = save_image(p["images"][0], f"{slug}.jpg")
            card = save_image(p["images"][1], f"{slug}-card.jpg") if len(p["images"]) > 1 else None
        except Exception as e:  # noqa: BLE001
            print(f"  skip {no}: image download failed ({e})")
            continue
        meta = derive_meta(it["title"], p)
        entry = {
            "slug": slug, "title": it["title"], **meta,
            "intro": p["intro"], "servings": p["servings"],
            "photo": photo, "photo_alt": f"{it['title']} 완성 사진",
            "ingredients": p["ingredients"], "steps": p["steps"], "tips": p["tips"], "closing": p["closing"],
            "naver_logno": no, "naver_hash": h, "source": "naver",
        }
        if card:
            entry.update({"card": card, "card_alt": f"{it['title']} 사진"})
            if p["has_ai"]:
                entry.update({"card_caption": "Photo — 직접 만든 한 접시", "card_is_photo": True})
        if p["has_ai"]:
            entry["photo_alt"] = f"{it['title']} 재료와 완성 접시를 담은 대표 이미지"
        new_entries.append(entry)
        changed = True
        print(f"  + {no} {it['title']} (새 레시피 추가)")
    if new_entries:
        recipes = new_entries + recipes
    if changed:
        with open(DATA, "w", encoding="utf-8") as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("CHANGED")
    else:
        print("NO CHANGES")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", help="저장된 글 HTML로 파서만 테스트")
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    if a.html:
        res = parse_post(open(a.html, encoding="utf-8").read(), a.title)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        if res:
            print(json.dumps(derive_meta(a.title, res), ensure_ascii=False, indent=2))
    else:
        sync()
