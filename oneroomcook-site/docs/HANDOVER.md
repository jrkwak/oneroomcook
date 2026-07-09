# 운영 · 인수인계 매뉴얼 (HANDOVER)

> 이 문서는 원룸쿡 웹사이트/브랜드를 제3자가 인수해도
> **하루 안에 운영을 시작할 수 있도록** 작성되었습니다.

## 1. 자산 목록 (매각 시 인계 범위)

| # | 자산 | 위치 / 계정 | 비고 |
|---|---|---|---|
| 1 | 도메인 | (구입 후 기입) | 레지스트라 계정 이전 |
| 2 | 웹사이트 코드 | 이 저장소 전체 | GitHub 저장소 이전 |
| 3 | 인스타그램 @oneroomcook | oneroomcook@gmail.com | 계정 소유권 이전 |
| 4 | 브랜드 자산 | docs/BRAND.md + assets/img/ | 로고·컬러·폰트 규정 |
| 5 | 레시피 콘텐츠 | data/recipes.json | 구조화 데이터 — 이전·재활용 용이 |
| 6 | 성장 지표 기록 | assets/js/metrics-data.js | 매월 실측 누적분 |
| 7 | 문의 폼 | Formspree 계정 | 수신 메일 주소 변경으로 이전 |

## 2. 정기 운영 루틴

| 주기 | 작업 | 파일 | 소요 |
|---|---|---|---|
| 콘텐츠 발행 시 | 레시피 추가 → `python3 scripts/build.py` → sitemap 1줄 추가 → push | data/recipes.json | 15분 |
| 매월 1일 | 인사이트 실측값 추가 | assets/js/metrics-data.js | 5분 |
| 분기 | 미디어킷 문구·패키지 점검 | partnership.html | 30분 |
| 수시 | 문의 응대 (2영업일 내 회신 원칙) | Formspree 수신함 | — |

## 3. 기술 스택 (의도적으로 단순함)

- 정적 HTML/CSS/JS. 빌드 도구·프레임워크·서버 없음.
- 유일한 스크립트: `scripts/build.py` (Python 3 표준 라이브러리만 사용)
- 외부 의존: Google Fonts(Noto Serif KR), jsDelivr(Pretendard), Formspree(폼), 선택적 IG 위젯
- 호스팅: GitHub Pages (무료). Netlify/Vercel/일반 웹호스팅으로 폴더 복사만으로 이전 가능.

## 4. 매각 준비 체크리스트

- [ ] 커스텀 도메인 확보 및 연결 (브랜드 검색량 축적 시작)
- [ ] 매월 실측 지표 12개월 이상 누적 (metrics-data.js)
- [ ] Google Search Console 검색 유입 데이터 축적
- [ ] 협업 이력·단가·결과 리포트 아카이빙 (docs/ 하위에 케이스 스터디로)
- [ ] 이메일(oneroomcook@gmail.com)을 브랜드 전용으로 유지 — 개인 용도 혼용 금지
- [ ] 레시피 사진을 SVG 플레이스홀더에서 실사진으로 순차 교체

## 5. 트러블슈팅

| 증상 | 원인/해결 |
|---|---|
| 폼 제출이 안 감 | contact.html의 YOUR_FORM_ID 미교체. README 5절 참고 |
| 차트가 안 보임 | metrics-data.js의 JSON 문법 오류 (콤마 누락 등). 브라우저 콘솔 확인 |
| 새 레시피가 아카이브에 없음 | build.py 미실행. `python3 scripts/build.py` |
| 리치 스니펫 미노출 | 색인에 수 주 소요. Search Console의 URL 검사 → 색인 요청 |
