/* ==========================================================================
   ONEROOMCOOK — main.js
   의존성 없는 바닐라 JS. (모바일 퍼포먼스를 위해 프레임워크 미사용)
   1) 모바일 내비게이션   2) 레시피 카테고리 필터
   3) 스크롤 리빌 애니메이션   4) 인스타그램 피드
   ========================================================================== */

/* 1) 모바일 내비게이션 --------------------------------------------------- */
(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.nav');
  if (!toggle || !nav) return;
  toggle.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
})();

/* 2) 레시피 카테고리 필터 ------------------------------------------------- */
(function () {
  var bar = document.querySelector('.filter-bar');
  if (!bar) return;
  var cards = Array.prototype.slice.call(document.querySelectorAll('.recipe-card'));
  var countEl = document.querySelector('.archive-count b');

  bar.addEventListener('click', function (e) {
    var btn = e.target.closest('.filter-btn');
    if (!btn) return;
    bar.querySelectorAll('.filter-btn').forEach(function (b) {
      b.classList.remove('active');
      b.setAttribute('aria-pressed', 'false');
    });
    btn.classList.add('active');
    btn.setAttribute('aria-pressed', 'true');

    var cat = btn.dataset.filter;
    var visible = 0;
    cards.forEach(function (card) {
      var show = cat === 'all' || (card.dataset.categories || '').split(' ').indexOf(cat) !== -1;
      card.classList.toggle('hidden', !show);
      if (show) visible++;
    });
    if (countEl) countEl.textContent = visible;
  });
})();

/* 3) 스크롤 리빌 ----------------------------------------------------------- */
(function () {
  var els = document.querySelectorAll('.reveal');
  if (!els.length || !('IntersectionObserver' in window)) {
    els.forEach(function (el) { el.classList.add('in'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  els.forEach(function (el) { io.observe(el); });
})();

/* 4) 인스타그램 피드 --------------------------------------------------------
   기본값: 로컬 플레이스홀더 이미지(assets/img/ig-*.svg)를 렌더링합니다.
   실서비스 연동 방법 (README.md의 "인스타그램 연동" 섹션 참고):
   - Behold.so / SnapWidget 등의 무료 위젯 서비스에서 발급받은
     피드 JSON URL을 아래 IG_FEED_URL에 넣으면 최신 게시물이 자동 표시됩니다.
   - Meta Graph API를 직접 쓰려면 서버(또는 GitHub Actions 크론)로
     data/instagram.json을 주기적으로 갱신하는 방식을 권장합니다.
   -------------------------------------------------------------------------- */
(function () {
  var grid = document.querySelector('[data-ig-grid]');
  if (!grid) return;

  var IG_FEED_URL = ''; // 예: 'https://feeds.behold.so/XXXXXXXX'
  var IG_PROFILE = 'https://www.instagram.com/oneroomcook/';
  var root = grid.dataset.root || '.';

  function renderPlaceholders() {
    var html = '';
    for (var i = 1; i <= 6; i++) {
      html += '<a href="' + IG_PROFILE + '" target="_blank" rel="noopener">' +
        '<img src="' + root + '/assets/img/ig-' + i + '.svg" alt="원룸쿡 인스타그램 게시물 미리보기 ' + i + '" loading="lazy" width="300" height="300"></a>';
    }
    grid.innerHTML = html;
  }

  if (!IG_FEED_URL) { renderPlaceholders(); return; }

  fetch(IG_FEED_URL)
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var posts = (data.posts || data).slice(0, 6);
      grid.innerHTML = posts.map(function (p) {
        var src = p.mediaUrl || p.thumbnailUrl || p.sizes && p.sizes.medium.mediaUrl;
        var link = p.permalink || IG_PROFILE;
        return '<a href="' + link + '" target="_blank" rel="noopener">' +
          '<img src="' + src + '" alt="원룸쿡 인스타그램 게시물" loading="lazy" width="300" height="300"></a>';
      }).join('');
    })
    .catch(renderPlaceholders);
})();
