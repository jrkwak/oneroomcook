/* ==========================================================================
   ONEROOMCOOK — site.js (v2.0)
   전 페이지 공통 인터랙션. 의존성 0. JS가 없어도 모든 콘텐츠는 정상 노출.
   1) 리빌  2) 헤더 스크롤 상태  3) 모바일 메뉴
   4) 카운트업  5) 코스 호버 썸네일  6) 레시피 필터
   ========================================================================== */
(function () {
  'use strict';
  document.documentElement.classList.add('js');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* 1) 리빌 ---------------------------------------------------------------- */
  var els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduced) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12 });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add('in'); });
  }

  /* 2) 헤더 스크롤 상태 ------------------------------------------------------ */
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () { header.classList.toggle('scrolled', window.scrollY > 10); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* 3) 모바일 메뉴 ----------------------------------------------------------- */
  var burger = document.querySelector('.burger');
  var menu = document.querySelector('.mobile-menu');
  if (burger && menu) {
    burger.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      document.body.classList.toggle('menu-open', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    menu.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') burger.click();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('open')) burger.click();
    });
  }

  /* 4) 카운트업 — HTML에 실제 숫자가 있고, JS는 연출만 담당 --------------------- */
  var counters = document.querySelectorAll('[data-count]');
  if (counters.length && 'IntersectionObserver' in window && !reduced) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        cio.unobserve(en.target);
        var el = en.target;
        var target = parseFloat(el.dataset.count);
        var dec = (el.dataset.count.split('.')[1] || '').length;
        var suffix = el.dataset.suffix || '';
        var t0 = null;
        function step(ts) {
          if (!t0) t0 = ts;
          var k = Math.min((ts - t0) / 1400, 1);
          k = 1 - Math.pow(1 - k, 3);
          var v = target * k;
          el.textContent = (dec ? v.toFixed(dec) : Math.round(v).toLocaleString()) + suffix;
          if (k < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
      });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { cio.observe(el); });
  }

  /* 5) 코스 호버 썸네일 (데스크톱 전용) ---------------------------------------- */
  var thumb = document.querySelector('.course-thumb');
  if (thumb && matchMedia('(hover: hover)').matches) {
    var img = thumb.querySelector('img');
    document.querySelectorAll('.course[data-img]').forEach(function (c) {
      c.addEventListener('mouseenter', function () {
        img.src = c.dataset.img; thumb.classList.add('show');
      });
      c.addEventListener('mouseleave', function () { thumb.classList.remove('show'); });
      c.addEventListener('mousemove', function (e) {
        thumb.style.left = Math.min(e.clientX + 28, window.innerWidth - 250) + 'px';
        thumb.style.top = (e.clientY - 90) + 'px';
      });
    });
  }

  /* 6) 레시피 카테고리 필터 --------------------------------------------------- */
  var bar = document.querySelector('.filter-bar');
  if (bar) {
    var cards = Array.prototype.slice.call(document.querySelectorAll('.dish-card'));
    var countEl = document.querySelector('.archive-count b');
    bar.addEventListener('click', function (e) {
      var btn = e.target.closest('button[data-filter]');
      if (!btn) return;
      bar.querySelectorAll('button').forEach(function (b) {
        b.classList.remove('active'); b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('active'); btn.setAttribute('aria-pressed', 'true');
      var cat = btn.dataset.filter, visible = 0;
      cards.forEach(function (card) {
        var show = cat === 'all' || (card.dataset.categories || '').split(' ').indexOf(cat) !== -1;
        card.classList.toggle('hidden', !show);
        if (show) visible++;
      });
      if (countEl) countEl.textContent = visible;
    });
  }
  /* 7) 인스타그램 피드 (Behold) ----------------------------------------------
     data-feed에 지정된 Behold JSON을 읽어 최신 게시물을 렌더.
     실패하면 섹션을 조용히 숨기고 프로필 링크만 남긴다. */
  var ig = document.querySelector('.ig-grid[data-feed]');
  if (ig && 'fetch' in window) {
    fetch(ig.dataset.feed)
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) {
        var posts = (data && (data.posts || data)) || [];
        if (!Array.isArray(posts) || !posts.length) throw new Error('empty');
        posts.slice(0, 6).forEach(function (p) {
          var src = (p.mediaType === 'VIDEO' && p.thumbnailUrl) ? p.thumbnailUrl : (p.mediaUrl || p.thumbnailUrl);
          if (!src) return;
          var a = document.createElement('a');
          a.href = p.permalink || 'https://www.instagram.com/oneroomcook/';
          a.target = '_blank'; a.rel = 'noopener';
          var img = document.createElement('img');
          img.src = src; img.loading = 'lazy'; img.width = 400; img.height = 400;
          img.alt = p.caption ? String(p.caption).slice(0, 110) : 'Instagram 게시물';
          a.appendChild(img);
          ig.appendChild(a);
        });
      })
      .catch(function () {
        var note = document.querySelector('.ig-note');
        if (note) note.innerHTML = '피드를 불러오지 못했습니다. <a href="https://www.instagram.com/oneroomcook/" target="_blank" rel="noopener">인스타그램에서 보기 →</a>';
        ig.style.display = 'none';
      });
  }
})();
