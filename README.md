# 원룸쿡 ONEROOMCOOK — v2.0

여섯 평의 파인다이닝. GitHub Pages용 정적 사이트 (빌드 도구 불필요, HTML/CSS/JS만).

## 무엇이 바뀌었나 (v1 → v2)

- **깨진 스타일 근본 해결** — 기존 `luxe.css`가 CDN/브라우저에 구버전으로 캐시되어 내부 페이지(Story·Contact·레시피)가 반쯤 깨져 보였습니다. 파일명을 `site.css?v=2`로 교체해 캐시 문제를 원천 차단하고, 전 13개 페이지가 하나의 스타일시트를 공유합니다.
- **실사 영상 스크럽 히어로** — 랜딩에서 스크롤하면 실사 슬로모션 영상(소금을 뿌리는 셰프의 손 → 김이 오르는 팬)이 스크롤 위치에 맞춰 프레임 단위로 재생됩니다 (Apple 제품 페이지 방식). 모바일·저사양·영상 로드 실패 시 사진 히어로로 자동 폴백.
- **사진 전면 교체** — 요리와 사진이 다르던 문제(크림파스타 페이지에 라면 사진 등)를 전부 실제 요리에 맞는 사진으로 교체.
- **스크롤 하이재킹 제거** — 프리로더, 커스텀 커서, 필름 그레인, 고정 스크럽 섹션 제거. 페이지가 "멈춘 것처럼" 느껴지던 원인.
- **Formspree 연동 완료** — 컨택 폼이 `xrewwnbv` 양식으로 실제 발송됩니다.
- **인스타그램 피드** — 홈 하단에 Behold 피드(최신 6개) 자동 표시. 실패 시 프로필 링크로 대체.
- **SEO/기술** — sitemap.xml, robots.txt, 404 페이지, 레시피 Recipe JSON-LD 유지, JS 없이도 전체 콘텐츠·수치 노출(크롤러가 "0 팔로워"를 보던 문제 해결), 인쇄용 레시피 스타일, 접근성(스킵 링크, 포커스 링, aria-current).

## 배포 방법

1. GitHub 저장소(`jrkwak/oneroomcook`)의 기존 파일을 **전부 삭제**합니다.
2. 이 폴더(`oneroomcook/`) 안의 내용물을 저장소 루트에 업로드하고 커밋합니다.
   - 웹에서: 저장소 → `Add file` → `Upload files` → 폴더 내용물 드래그.
3. 1–2분 후 https://jrkwak.github.io/oneroomcook/ 에서 확인. 이전 화면이 보이면 `Ctrl+Shift+R`(강력 새로고침).

## 운영 가이드

- **월간 지표 갱신**: `assets/js/metrics-data.js`의 숫자만 수정하면 파트너십 대시보드가 자동으로 다시 그려집니다. 홈/파트너십의 큰 수치 4개는 `index.html`·`partnership.html`에서 `data-count` 값과 표시 텍스트를 함께 수정하세요.
- **레시피 추가**: `recipes/` 안의 아무 파일이나 복제해 내용을 바꾸고, `recipes/index.html`에 카드 하나, `sitemap.xml`에 URL 한 줄을 추가하면 됩니다.
- **컨택 폼**: Formspree 대시보드(https://formspree.io)에서 수신 확인. 알림 이메일은 oneroomcook@gmail.com.
- **인스타 피드**: Behold(https://behold.so) 대시보드에서 피드 관리. 피드 URL 변경 시 `index.html`의 `data-feed` 값만 교체.
- **히어로 영상 교체**: 새 영상을 `ffmpeg -i 원본.mp4 -vf scale=1440:-2 -an -c:v libx264 -preset slow -crf 23 -g 1 -pix_fmt yuv420p -movflags +faststart hero-scrub.mp4` 로 인코딩해 `assets/video/hero-scrub.mp4` 교체 (`-g 1` 전 프레임 키프레임이 핵심 — 스크럽이 부드러워지는 이유). 포스터는 `assets/img/hero-poster.jpg`.
- **히어로 캡션/타이밍**: 캡션 문구는 `index.html`의 `.h3d-cap`, 등장 타이밍은 `assets/js/hero-scrub.js`의 `CAP_C` 배열, 스크롤 분량은 `site.css`의 `.hero3d.on { height: 380vh; }`

## 구조

```
index.html            홈 (3D 히어로 + 시그니처 + 코스 + 지표 + 인스타)
about.html            스토리
partnership.html      미디어킷 (성장 대시보드 SVG 차트)
contact.html          협업 문의 (Formspree)
404.html              404
recipes/              레시피 아카이브 + 상세 8개 (Recipe JSON-LD)
assets/css/site.css   전 페이지 공용 스타일
assets/js/site.js     공용 인터랙션 (메뉴·리빌·카운트업·필터·인스타 피드)
assets/js/hero-scrub.js    실사 영상 스크럽 히어로
assets/video/hero-scrub.mp4  히어로 영상 (전 프레임 키프레임 인코딩)
assets/js/metrics-data.js  월간 지표 데이터
sitemap.xml · robots.txt · favicon.svg
```
