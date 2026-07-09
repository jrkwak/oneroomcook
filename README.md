# 원룸쿡 ONEROOMCOOK — 공식 웹사이트

> 좁은 원룸, 최소한의 장비로 차린 근사한 한 끼.
> 인스타그램 [@oneroomcook](https://www.instagram.com/oneroomcook/)의 공식 웹사이트이자,
> 협업·매각을 염두에 둔 **미디어 브랜드 자산**입니다.

프레임워크·빌드 도구 없는 **순수 정적 사이트**입니다. HTML/CSS/JS만 알면 누구든 유지보수할 수 있고, 어떤 호스팅으로든 이전할 수 있습니다. (인수인계를 쉽게 하기 위한 의도적 선택입니다.)

---

## 1. 폴더 구조

```
oneroomcook-site/
├── index.html              # 홈 (히어로 · 대표 레시피 · 스토리 · IG 피드)
├── about.html              # 브랜드 스토리
├── partnership.html        # 미디어킷 + 성장 대시보드 (광고주 대상)
├── contact.html            # 협업 문의 폼 (Formspree)
├── 404.html                # 커스텀 404
├── favicon.svg / sitemap.xml / robots.txt
├── recipes/
│   ├── index.html          # 레시피 아카이브 (카테고리 필터)
│   └── <slug>.html         # 레시피 상세 ×8 (Recipe JSON-LD 포함)
├── assets/
│   ├── css/style.css       # 전체 스타일 (목차 주석 참고)
│   ├── js/main.js          # 내비 · 필터 · 리빌 · IG 피드
│   ├── js/metrics-data.js  # ★ 대시보드 지표 (매월 여기만 수정)
│   └── img/                # 로고 · 일러스트 (SVG)
├── data/recipes.json       # ★ 레시피 원본 데이터 (단일 소스)
├── scripts/build.py        # recipes.json → HTML/SVG 생성기
└── docs/
    ├── BRAND.md            # 브랜드 가이드 (컬러 · 폰트 · 로고 · 보이스)
    └── HANDOVER.md         # 운영 · 인수인계 매뉴얼
```

## 2. 배포 (GitHub Pages)

현재 배포 주소: **https://jrkwak.github.io/oneroomcook/** (저장소: `jrkwak/oneroomcook`)

1. 저장소에 이 폴더의 **내용물 전체**를 업로드 (index.html이 저장소 루트에 오도록)
2. Settings → Pages → Source: `Deploy from a branch`, Branch: `main` / `/ (root)` → Save
3. 1~3분 후 위 주소에서 확인

**커스텀 도메인 연결 시** (예: `oneroomcook.com` — 매각 가치를 위해 조기 확보 권장):
1. 도메인 등록 후 DNS에 GitHub Pages IP(A 레코드) 또는 CNAME 설정
2. Settings → Pages → Custom domain 입력, Enforce HTTPS 체크
3. 저장소 루트에 도메인만 적힌 `CNAME` 파일 추가
4. **전체 파일에서 `https://jrkwak.github.io/oneroomcook` 를 새 도메인으로 일괄 치환**
   (canonical, og:url, sitemap.xml, robots.txt, scripts/build.py의 BASE_URL)

## 3. 레시피 추가·수정 (가장 자주 하는 일)

1. `data/recipes.json`에 항목 추가 (기존 항목 복사 후 수정이 가장 쉬움)
2. `python3 scripts/build.py` 실행 → 상세 페이지·아카이브·일러스트 자동 생성
3. `sitemap.xml`에 새 URL 한 줄 추가
4. 실제 요리 사진이 준비되면 `assets/img/`의 해당 SVG를 같은 이름의 JPG/WebP로 교체하고 HTML의 확장자만 수정 (권장: 1200×900, WebP, 200KB 이하)

## 4. 미디어킷 대시보드 갱신 (매월 1일)

`assets/js/metrics-data.js` 하나만 수정하면 파트너십 페이지 차트가 자동 반영됩니다.
인스타그램 프로페셔널 대시보드 → 인사이트에서 팔로워 수·참여율을 확인해 배열 끝에 추가하세요.

> ⚠️ 현재 과거 추이는 성장 곡선 기반 **추정 백필**이고, 2026-07 값(팔로워 1,990 / 게시물 39)만 실측입니다.
> 매각 실사(Due Diligence) 때는 실측 데이터가 필수이므로, 지금부터 매월 실측값을 쌓는 것이 곧 자산 가치입니다.

## 5. 문의 폼 연동 (Formspree)

1. [formspree.io](https://formspree.io)에 `oneroomcook@gmail.com`으로 가입
2. New Form 생성 → 발급된 Form ID 복사
3. `contact.html`의 `action="https://formspree.io/f/YOUR_FORM_ID"`에서 `YOUR_FORM_ID` 교체
- 무료 플랜: 월 50건 (초기에 충분). 스팸 방지용 허니팟(`_gotcha`) 적용 완료.

## 6. 인스타그램 피드 연동

기본값은 브랜드 톤의 플레이스홀더 6장입니다. 실연동은 두 가지 방법:

| 방법 | 난이도 | 비고 |
|---|---|---|
| **Behold.so / SnapWidget** (권장) | 쉬움 | 무료 플랜으로 피드 JSON URL 발급 → `assets/js/main.js`의 `IG_FEED_URL`에 입력 |
| Meta Graph API 직접 연동 | 중간 | 토큰 갱신 필요. GitHub Actions 크론으로 `data/instagram.json` 주기 갱신 방식 권장 |

## 7. SEO 체크리스트 (세팅 완료 항목)

- [x] 페이지별 title / meta description / canonical / OG 태그
- [x] 레시피 전 페이지 **Recipe JSON-LD** (리치 스니펫 대상) + Organization/WebSite 스키마
- [x] sitemap.xml / robots.txt / 시맨틱 마크업 / 전 이미지 alt 텍스트
- [x] 모바일 최적화: 프레임워크 0, JS 1개(지연 로드), SVG 이미지, lazy loading, 폰트 subset+swap
- [ ] 배포 후 할 일: Google Search Console·네이버 서치어드바이저에 sitemap 제출, OG 대표 이미지(`assets/img/og-cover.png`, 1200×630) 실사진으로 제작

> 참고: Recipe 스키마에 평점(aggregateRating)은 **넣지 않았습니다**. 실제 사용자 평점 없이 넣으면 구글 가이드라인 위반으로 오히려 페널티 대상입니다. 후일 댓글/평점 기능 도입 시 추가하세요.

## 8. 브랜드 자산 패키지 (매각 대비)

`docs/BRAND.md`에 로고·컬러·타이포·보이스 가이드가 정리되어 있습니다.
매각 협상 시 인계 대상: ① 도메인 ② 이 저장소 전체 ③ 인스타그램 계정 ④ BRAND.md 기준 브랜드 자산 ⑤ 월별 실측 지표 기록. 상세 절차는 `docs/HANDOVER.md` 참고.
