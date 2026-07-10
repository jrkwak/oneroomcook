/* ==========================================================================
   ONEROOMCOOK — hero-scrub.js (v2.1)
   실사 영상 스크롤 스크럽 히어로 (Apple 제품 페이지 방식).
   스크롤 위치 = 영상 타임라인. 전 프레임 키프레임으로 인코딩된
   assets/video/hero-scrub.mp4 를 프레임 단위로 탐색한다.
   - 모바일(≤640px) / 저사양 / 영상 로드 실패 시 → 사진 히어로 폴백
   - prefers-reduced-motion: 스크럽은 사용자 주도 모션이라 유지
   ========================================================================== */
(function () {
  'use strict';

  var section = document.getElementById('hero3d');
  var video = document.getElementById('hero-scrub-video');
  if (!section || !video) return;

  var small = window.matchMedia('(max-width: 640px)').matches;
  var lowCpu = typeof navigator.hardwareConcurrency === 'number' && navigator.hardwareConcurrency < 4;
  if (small || lowCpu) return; // 사진 폴백 유지

  var title = section.querySelector('.h3d-title');
  var caps = Array.prototype.slice.call(section.querySelectorAll('.h3d-cap'));
  var hint = section.querySelector('.h3d-hint');
  var CAP_C = [0.22, 0.44, 0.66, 0.88];
  var CAP_W = 0.115;

  var progress = 0, inView = true, duration = 0;
  var tNow = 0, started = false;

  function readScroll() {
    var rect = section.getBoundingClientRect();
    var total = rect.height - window.innerHeight;
    progress = total > 0 ? Math.min(Math.max(-rect.top / total, 0), 1) : 0;
    inView = rect.bottom > -80 && rect.top < window.innerHeight + 80;
  }

  function smooth(t) { return t * t * (3 - 2 * t); }

  function frame() {
    requestAnimationFrame(frame);
    if (!inView || !duration) return;
    var r = progress;

    /* 타임라인 스크럽 (감쇠 추적으로 부드럽게) */
    var target = r * (duration - 0.08);
    tNow += (target - tNow) * 0.16;
    if (Math.abs(video.currentTime - tNow) > 0.01 && video.readyState >= 2) {
      try { video.currentTime = tNow; } catch (e) {}
    }

    /* 오버레이 */
    if (title) {
      var to = r < 0.1 ? 1 - r / 0.1 : 0;
      title.style.opacity = to.toFixed(3);
      title.style.pointerEvents = to > 0.4 ? 'auto' : 'none';
    }
    if (hint) hint.style.opacity = (r < 0.06 ? 1 : Math.max(0, 1 - (r - 0.06) / 0.05)).toFixed(3);
    for (var c = 0; c < caps.length; c++) {
      var dist = Math.abs(r - CAP_C[c]);
      var o = Math.max(0, 1 - dist / CAP_W);
      caps[c].style.opacity = smooth(o).toFixed(3);
    }
  }

  function activate() {
    if (started) return;
    started = true;
    duration = video.duration || 0;
    section.classList.add('on');
    document.documentElement.classList.add('hero3d-on');
    video.pause();
    try { video.currentTime = 0; } catch (e) {}
    window.addEventListener('scroll', readScroll, { passive: true });
    window.addEventListener('resize', readScroll);
    readScroll();
    frame();
  }

  video.preload = 'auto';
  video.addEventListener('loadedmetadata', activate);
  video.addEventListener('error', function () { /* 폴백: on 클래스 미부여 → 사진 유지 */ });
  if (video.readyState >= 1) activate();
  video.load();
})();
