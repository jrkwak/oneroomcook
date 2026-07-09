/* ==========================================================================
   ONEROOMCOOK — cinema.js
   Apple식 scroll-driven 연출: 스크롤 위치가 곧 타임라인.
   1) 요리의 4막(크로스페이드+스케일 스크럽)  2) 회전 플레이트  3) 히어로 패럴랙스
   ========================================================================== */
(function () {
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function ease(t) { return t * t * (3 - 2 * t); } // smoothstep

  /* 1) 요리의 4막 스크럽 --------------------------------------------------- */
  var seq = document.querySelector('[data-scrub="acts"]');
  var acts = seq ? Array.prototype.slice.call(seq.querySelectorAll('.act')) : [];
  var dots = seq ? Array.prototype.slice.call(seq.querySelectorAll('.scrub-progress i')) : [];

  function renderActs() {
    if (!seq || !acts.length) return;
    var rect = seq.getBoundingClientRect();
    var total = rect.height - window.innerHeight;
    var p = clamp(-rect.top / total, 0, 1);
    var n = acts.length;
    var seg = 1 / n;
    acts.forEach(function (act, i) {
      var local = clamp((p - i * seg) / seg, 0, 1);   // 이 막 안에서의 진행도
      var fadeIn = i === 0 ? 1 : ease(clamp(local / 0.35, 0, 1));   // 앞 35%에서 등장
      var fadeOut = i < n - 1 ? 1 - ease(clamp((local - 0.65) / 0.35, 0, 1)) : 1; // 뒤 35%에서 퇴장
      var active = p >= i * seg && p < (i + 1) * seg || (i === n - 1 && p >= 1 - seg);
      act.style.opacity = (fadeIn * fadeOut).toFixed(3);
      act.style.zIndex = active ? 2 : 1;
      var img = act.querySelector('img');
      if (img) img.style.transform = 'scale(' + (1.14 - 0.10 * local) + ')';
      var cap = act.querySelector('.act-caption');
      if (cap) {
        cap.style.opacity = (fadeIn * fadeOut).toFixed(3);
        // 캡션이 막 전체에 걸쳐 계속 떠오르도록 — 정지감 제거
        cap.style.transform = 'translateY(' + (36 - local * 66) + 'px)';
      }
      if (dots[i]) dots[i].classList.toggle('on', active);
    });
  }

  /* 2) 회전 플레이트 --------------------------------------------------------- */
  var plateSec = document.querySelector('[data-scrub="plate"]');
  var plateImg = plateSec ? plateSec.querySelector('.plate-wrap img') : null;

  function renderPlate() {
    if (!plateSec || !plateImg) return;
    var rect = plateSec.getBoundingClientRect();
    var total = rect.height - window.innerHeight;
    var p = clamp(-rect.top / total, 0, 1);
    var deg = p * 240 - 120;               // -120° → +120° 회전
    var sc = 0.82 + ease(clamp(p * 2, 0, 1)) * 0.18;
    plateImg.style.transform = 'rotate(' + deg + 'deg) scale(' + sc + ')';
  }

  /* 3) 히어로 패럴랙스 -------------------------------------------------------- */
  var heroImg = document.querySelector('.photo-hero .ph-img');
  function renderHero() {
    if (!heroImg) return;
    var y = clamp(window.scrollY / window.innerHeight, 0, 1);
    heroImg.style.opacity = (1 - y * 0.55).toFixed(3);
  }

  if (reduced) {
    acts.forEach(function (a, i) { a.style.opacity = i === 0 ? 1 : 0; });
    if (acts[0]) { var c = acts[0].querySelector('.act-caption'); if (c) c.style.opacity = 1; }
    return;
  }
  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      renderActs(); renderPlate(); renderHero();
      ticking = false;
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  onScroll();
})();
