/* ==========================================================================
   ONEROOMCOOK — luxe.js
   랜딩 전용 모션 엔진 (의존성 0)
   1) 프리로더  2) 커스텀 커서  3) 실시간 파티클(김+골드 더스트, Canvas 2D)
   4) 패럴랙스  5) 리빌  6) 코스 호버 썸네일  7) 카운트업
   ========================================================================== */
(function () {
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* 1) 프리로더 ----------------------------------------------------------- */
  var pre = document.querySelector('.preloader');
  if (pre) {
    window.addEventListener('load', function () {
      setTimeout(function () { pre.classList.add('done'); }, reduced ? 0 : 1900);
    });
    setTimeout(function () { pre.classList.add('done'); }, 3500); // 안전장치
  }

  /* 2) 커스텀 커서 --------------------------------------------------------- */
  var dot = document.querySelector('.cursor-dot');
  var ring = document.querySelector('.cursor-ring');
  if (dot && ring && matchMedia('(hover: hover)').matches) {
    var mx = -100, my = -100, rx = -100, ry = -100;
    document.addEventListener('mousemove', function (e) { mx = e.clientX; my = e.clientY; });
    (function loop() {
      rx += (mx - rx) * 0.16; ry += (my - ry) * 0.16;
      dot.style.transform = 'translate(' + mx + 'px,' + my + 'px) translate(-50%,-50%)';
      ring.style.transform = 'translate(' + rx + 'px,' + ry + 'px) translate(-50%,-50%)';
      requestAnimationFrame(loop);
    })();
    document.querySelectorAll('a, button, .course').forEach(function (el) {
      el.addEventListener('mouseenter', function () { ring.classList.add('is-hover'); });
      el.addEventListener('mouseleave', function () { ring.classList.remove('is-hover'); });
    });
  }

  /* 3) 실시간 파티클: 피어오르는 김 + 골드 더스트 ---------------------------- */
  var canvas = document.getElementById('steam-canvas');
  if (canvas && !reduced) {
    var ctx = canvas.getContext('2d');
    var W1, H1, DPR = Math.min(window.devicePixelRatio || 1, 2);
    var mouse = { x: -9999, y: -9999 };
    var isMobile = matchMedia('(pointer: coarse)').matches;
    var N = isMobile ? 42 : 90;
    var parts = [];

    function resize() {
      W1 = canvas.clientWidth; H1 = canvas.clientHeight;
      canvas.width = W1 * DPR; canvas.height = H1 * DPR;
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    }
    resize();
    window.addEventListener('resize', resize);
    canvas.parentElement.addEventListener('mousemove', function (e) {
      var r = canvas.getBoundingClientRect();
      mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top;
    });
    canvas.parentElement.addEventListener('mouseleave', function () { mouse.x = mouse.y = -9999; });

    function spawn(p, first) {
      p.gold = Math.random() < 0.45;                 // 골드 더스트 or 김
      p.x = Math.random() * W1;
      p.y = first ? Math.random() * H1 : H1 + 20;
      p.r = p.gold ? (Math.random() * 1.6 + 0.6) : (Math.random() * 26 + 14);
      p.vy = -(Math.random() * 0.5 + (p.gold ? 0.25 : 0.12));
      p.vx = (Math.random() - 0.5) * 0.2;
      p.life = 0;
      p.max = Math.random() * 400 + 260;
      p.sway = Math.random() * Math.PI * 2;
      return p;
    }
    for (var i = 0; i < N; i++) parts.push(spawn({}, true));

    var running = true;
    document.addEventListener('visibilitychange', function () { running = !document.hidden; });

    (function frame() {
      requestAnimationFrame(frame);
      if (!running) return;
      ctx.clearRect(0, 0, W1, H1);
      for (var i = 0; i < parts.length; i++) {
        var p = parts[i];
        p.life++; p.sway += 0.012;
        p.x += p.vx + Math.sin(p.sway) * 0.25;
        p.y += p.vy;
        // 마우스 반발 — 김이 손을 피해가는 느낌
        var dx = p.x - mouse.x, dy = p.y - mouse.y, d2 = dx * dx + dy * dy;
        if (d2 < 16000) { var f = (16000 - d2) / 16000; p.x += (dx / Math.sqrt(d2 + 1)) * f * 2.4; p.y += (dy / Math.sqrt(d2 + 1)) * f * 2.4; }
        var t = p.life / p.max;
        var a = t < 0.15 ? t / 0.15 : (1 - t);
        if (t >= 1 || p.y < -60) { spawn(p); continue; }
        if (p.gold) {
          ctx.globalAlpha = a * 0.9;
          ctx.fillStyle = '#E4CE9E';
          ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill();
        } else {
          var g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r);
          g.addColorStop(0, 'rgba(244,238,226,' + (a * 0.05) + ')');
          g.addColorStop(1, 'rgba(244,238,226,0)');
          ctx.globalAlpha = 1; ctx.fillStyle = g;
          ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill();
        }
      }
      ctx.globalAlpha = 1;
    })();
  }

  /* 4) 패럴랙스 (히어로 백타이포 + data-parallax 요소) ------------------------ */
  if (!reduced) {
    var pxEls = document.querySelectorAll('[data-parallax]');
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        var y = window.scrollY;
        pxEls.forEach(function (el) {
          var speed = parseFloat(el.dataset.parallax) || 0.2;
          el.style.transform = 'translateY(' + (y * speed) + 'px)';
        });
        ticking = false;
      });
    }, { passive: true });
  }

  /* 5) 리빌 ----------------------------------------------------------------- */
  var els = document.querySelectorAll('.lx-reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.15 });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add('in'); }); }

  /* 6) 코스 호버 썸네일 — 커서를 따라오는 이미지 ------------------------------ */
  var thumb = document.querySelector('.course-thumb');
  if (thumb && matchMedia('(hover: hover)').matches) {
    var img = thumb.querySelector('img');
    document.querySelectorAll('.course').forEach(function (c) {
      c.addEventListener('mouseenter', function () {
        img.src = c.dataset.img; thumb.classList.add('show');
      });
      c.addEventListener('mouseleave', function () { thumb.classList.remove('show'); });
      c.addEventListener('mousemove', function (e) {
        thumb.style.left = (e.clientX + 30) + 'px';
        thumb.style.top = (e.clientY - 90) + 'px';
      });
    });
  }

  /* 7) 카운트업 --------------------------------------------------------------- */
  var counters = document.querySelectorAll('[data-count]');
  if (counters.length && 'IntersectionObserver' in window && !reduced) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        cio.unobserve(en.target);
        var el = en.target, target = parseFloat(el.dataset.count),
            dec = (el.dataset.count.split('.')[1] || '').length,
            suffix = el.dataset.suffix || '', t0 = null;
        function step(ts) {
          if (!t0) t0 = ts;
          var k = Math.min((ts - t0) / 1600, 1);
          k = 1 - Math.pow(1 - k, 3);
          var v = target * k;
          el.textContent = (dec ? v.toFixed(dec) : Math.round(v).toLocaleString()) + suffix;
          if (k < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
      });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { cio.observe(el); });
  } else {
    counters.forEach(function (el) {
      var v = parseFloat(el.dataset.count);
      el.textContent = (el.dataset.count.indexOf('.') > -1 ? v.toFixed(1) : v.toLocaleString()) + (el.dataset.suffix || '');
    });
  }
})();
