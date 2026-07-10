/* ==========================================================================
   ONEROOMCOOK — hero3d.js (v2.0)
   스크롤 연동 3D 히어로: 1구 인덕션 위 프라이팬이 스크롤할수록
   재료를 힘차게 토스하고, 카메라가 와이드 → 팬 클로즈업으로 돌리인.
   - three.js (CDN ES module) · 의존성 그 외 0
   - 모바일(≤640px) / 저사양 / prefers-reduced-motion / WebGL 실패 시
     → 기존 사진 히어로로 자동 폴백
   ========================================================================== */
(async function () {
  'use strict';

  var section = document.getElementById('hero3d');
  if (!section) return;

  /* calm: 모션 감소 설정 시에도 스크롤 연동(사용자 주도)은 유지하되
     자동 토스·플리커 같은 상시 모션만 정지 */
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var small = window.matchMedia('(max-width: 640px)').matches;
  var lowCpu = typeof navigator.hardwareConcurrency === 'number' && navigator.hardwareConcurrency < 4;
  if (small || lowCpu) return; // 사진 폴백 유지

  var THREE;
  try {
    THREE = await import('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js');
  } catch (e) { return; }

  var canvas = document.getElementById('hero3d-canvas');
  if (!canvas) return;

  var renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, powerPreference: 'high-performance' });
  } catch (e) { return; }

  /* 3D 모드 활성화 (실패 지점 이후에만 클래스 부여 → 그 전 실패는 폴백) */
  section.classList.add('on');
  document.documentElement.classList.add('hero3d-on');

  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
  renderer.shadowMap.enabled = false;

  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b0a09);
  scene.fog = new THREE.Fog(0x0b0a09, 6.5, 13);

  var camera = new THREE.PerspectiveCamera(42, 2, 0.1, 40);

  /* ------------------------------------------------------------------ 조명 */
  scene.add(new THREE.AmbientLight(0xf4eee2, 0.32));
  var key = new THREE.DirectionalLight(0xf5d8a6, 1.25);
  key.position.set(3, 4.2, 2.4);
  scene.add(key);
  var rim = new THREE.DirectionalLight(0xc9a96a, 0.55);
  rim.position.set(-2.6, 2.2, -3);
  scene.add(rim);
  var flame = new THREE.PointLight(0xff7a2f, 1.6, 5.5, 2);
  flame.position.set(0, 0.32, 0);
  scene.add(flame);

  /* --------------------------------------------------------------- 조리대 */
  var counterMat = new THREE.MeshStandardMaterial({ color: 0x171310, roughness: 0.85, metalness: 0.1 });
  var counter = new THREE.Mesh(new THREE.BoxGeometry(9, 0.5, 5.5), counterMat);
  counter.position.y = -0.27;
  scene.add(counter);

  /* 뒷벽 (은은한 콜 톤) */
  var wall = new THREE.Mesh(
    new THREE.BoxGeometry(12, 6, 0.2),
    new THREE.MeshStandardMaterial({ color: 0x14120f, roughness: 1 })
  );
  wall.position.set(0, 2.5, -2.9);
  scene.add(wall);

  /* 인덕션 */
  var hob = new THREE.Mesh(
    new THREE.CylinderGeometry(1.5, 1.5, 0.07, 64),
    new THREE.MeshStandardMaterial({ color: 0x0a0a0c, roughness: 0.25, metalness: 0.4 })
  );
  hob.position.y = 0.035;
  scene.add(hob);
  var hobRing = new THREE.Mesh(
    new THREE.TorusGeometry(1.5, 0.012, 12, 96),
    new THREE.MeshStandardMaterial({ color: 0xc9a96a, roughness: 0.35, metalness: 0.8 })
  );
  hobRing.rotation.x = Math.PI / 2;
  hobRing.position.y = 0.072;
  scene.add(hobRing);

  /* 히트 글로우 (팬 아래 발광 디스크) */
  var glow = new THREE.Mesh(
    new THREE.CircleGeometry(0.95, 48),
    new THREE.MeshBasicMaterial({ color: 0xff5a1f, transparent: true, opacity: 0.35 })
  );
  glow.rotation.x = -Math.PI / 2;
  glow.position.y = 0.075;
  scene.add(glow);

  /* ------------------------------------------------------------------- 팬 */
  var pan = new THREE.Group();
  var steel = new THREE.MeshStandardMaterial({ color: 0x2b2b30, roughness: 0.38, metalness: 0.85, side: THREE.DoubleSide });
  var panWall = new THREE.Mesh(new THREE.CylinderGeometry(1.08, 0.88, 0.3, 56, 1, true), steel);
  panWall.position.y = 0.15;
  pan.add(panWall);
  var panBase = new THREE.Mesh(new THREE.CircleGeometry(0.88, 56), steel);
  panBase.rotation.x = -Math.PI / 2;
  panBase.position.y = 0.005;
  pan.add(panBase);
  var panRim = new THREE.Mesh(
    new THREE.TorusGeometry(1.08, 0.022, 12, 72),
    new THREE.MeshStandardMaterial({ color: 0xc9a96a, roughness: 0.3, metalness: 0.9 })
  );
  panRim.rotation.x = Math.PI / 2;
  panRim.position.y = 0.3;
  pan.add(panRim);
  var handle = new THREE.Mesh(
    new THREE.CylinderGeometry(0.055, 0.07, 1.5, 16),
    new THREE.MeshStandardMaterial({ color: 0x17130f, roughness: 0.7, metalness: 0.2 })
  );
  handle.rotation.z = Math.PI / 2 - 0.12;
  handle.position.set(-1.75, 0.34, 0);
  pan.add(handle);
  var handleCap = new THREE.Mesh(
    new THREE.CylinderGeometry(0.075, 0.075, 0.05, 16),
    new THREE.MeshStandardMaterial({ color: 0xc9a96a, roughness: 0.35, metalness: 0.85 })
  );
  handleCap.rotation.z = Math.PI / 2 - 0.12;
  handleCap.position.set(-2.5, 0.43, 0);
  pan.add(handleCap);
  pan.position.y = 0.16;
  scene.add(pan);

  /* ------------------------------------------------------------- 재료 토스 */
  var foods = [];
  var foodDefs = [
    { geo: new THREE.BoxGeometry(0.13, 0.13, 0.13), color: 0xf4eee2, rough: 0.55, n: 4 },  // 두부
    { geo: new THREE.SphereGeometry(0.085, 20, 16), color: 0xc2452d, rough: 0.4, n: 4 },   // 방울토마토
    { geo: new THREE.CylinderGeometry(0.03, 0.03, 0.2, 10), color: 0x6a8f4f, rough: 0.6, n: 4 }, // 파
    { geo: new THREE.BoxGeometry(0.12, 0.05, 0.12), color: 0xb98a52, rough: 0.6, n: 4 },   // 양송이 슬라이스
  ];
  foodDefs.forEach(function (d) {
    for (var i = 0; i < d.n; i++) {
      var m = new THREE.Mesh(d.geo, new THREE.MeshStandardMaterial({ color: d.color, roughness: d.rough, metalness: 0.05 }));
      var item = {
        mesh: m,
        phase: Math.random(),
        r0: Math.random() * 0.55,               // 팬 안 반경
        a0: Math.random() * Math.PI * 2,        // 팬 안 각도
        h: 0.9 + Math.random() * 0.7,           // 토스 최고 높이 계수
        spin: new THREE.Vector3(Math.random() - 0.5, Math.random() - 0.5, Math.random() - 0.5).multiplyScalar(6),
        drift: (Math.random() - 0.5) * 0.5,
      };
      foods.push(item);
      scene.add(m);
    }
  });

  /* ------------------------------------------------------------------ 스팀 */
  var steamTex = (function () {
    var c = document.createElement('canvas'); c.width = c.height = 64;
    var ctx = c.getContext('2d');
    var g = ctx.createRadialGradient(32, 32, 2, 32, 32, 30);
    g.addColorStop(0, 'rgba(244,238,226,.55)');
    g.addColorStop(1, 'rgba(244,238,226,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, 64, 64);
    return new THREE.CanvasTexture(c);
  })();
  var steams = [];
  for (var s = 0; s < 22; s++) {
    var sp = new THREE.Sprite(new THREE.SpriteMaterial({
      map: steamTex, transparent: true, opacity: 0, depthWrite: false,
      blending: THREE.AdditiveBlending,
    }));
    sp.scale.setScalar(0.3);
    steams.push({ sp: sp, t: Math.random(), speed: 0.28 + Math.random() * 0.3, x: (Math.random() - 0.5) * 1.2, z: (Math.random() - 0.5) * 1.2 });
    scene.add(sp);
  }

  /* ------------------------------------------------------- 카메라 키프레임 */
  var KF = [
    { r: 0.00, pos: [0.0, 2.7, 6.6], look: [0, 0.7, 0], fov: 42 },
    { r: 0.34, pos: [2.7, 1.5, 3.1], look: [0, 0.65, 0], fov: 40 },
    { r: 0.67, pos: [1.15, 1.75, 1.65], look: [0, 0.6, 0], fov: 36 },
    { r: 1.00, pos: [0.05, 3.1, 0.95], look: [0, 0.45, 0], fov: 30 },
  ];
  function smooth(t) { return t * t * (3 - 2 * t); }
  function camAt(r, out) {
    var i = 0;
    while (i < KF.length - 2 && r > KF[i + 1].r) i++;
    var a = KF[i], b = KF[i + 1];
    var t = smooth(Math.min(Math.max((r - a.r) / (b.r - a.r), 0), 1));
    for (var k = 0; k < 3; k++) {
      out.pos[k] = a.pos[k] + (b.pos[k] - a.pos[k]) * t;
      out.look[k] = a.look[k] + (b.look[k] - a.look[k]) * t;
    }
    out.fov = a.fov + (b.fov - a.fov) * t;
  }
  var camTarget = { pos: [0, 0, 0], look: [0, 0, 0], fov: 42 };
  var camNow = { pos: KF[0].pos.slice(), look: KF[0].look.slice(), fov: KF[0].fov };

  /* ------------------------------------------------------ 오버레이 캡션 */
  var title = section.querySelector('.h3d-title');
  var caps = Array.prototype.slice.call(section.querySelectorAll('.h3d-cap'));
  var hint = section.querySelector('.h3d-hint');
  var CAP_C = [0.22, 0.44, 0.66, 0.88];
  var CAP_W = 0.115;

  /* ----------------------------------------------------------- 스크롤 진행 */
  var progress = 0, inView = true;
  function readScroll() {
    var rect = section.getBoundingClientRect();
    var total = rect.height - window.innerHeight;
    progress = total > 0 ? Math.min(Math.max(-rect.top / total, 0), 1) : 0;
    inView = rect.bottom > -80 && rect.top < window.innerHeight + 80;
  }
  window.addEventListener('scroll', readScroll, { passive: true });

  function resize() {
    var w = section.clientWidth, h = window.innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    readScroll();
  }
  window.addEventListener('resize', resize);
  resize();

  /* --------------------------------------------------------------- 루프 */
  var clock = new THREE.Clock();
  var T = 2.4; // 토스 주기(초)

  function frame() {
    requestAnimationFrame(frame);
    if (!inView) return;
    var t = clock.getElapsedTime();
    var r = progress;

    /* 토스 강도: 스크롤할수록 세게 (calm 모드에서는 상시 모션 정지) */
    var amp = calm ? 0 : 0.3 + r * 1.05;

    /* 팬 플릭 */
    var pg = (t / T) % 1;
    var flick = calm ? 0 : Math.sin(pg * Math.PI * 2);
    flick = flick * flick * flick;
    pan.rotation.z = -0.085 * flick * (0.5 + amp * 0.5);
    pan.position.y = 0.16 + Math.max(0, flick) * 0.05 * amp;

    /* 재료 */
    for (var i = 0; i < foods.length; i++) {
      var f = foods[i], m = f.mesh;
      var p = ((t / T) + f.phase) % 1;
      var bx = Math.cos(f.a0) * f.r0, bz = Math.sin(f.a0) * f.r0;
      if (p < 0.32) { // 팬 안에서 대기 (지글지글)
        m.position.set(bx, pan.position.y + 0.1 + Math.abs(Math.sin(t * 9 + i)) * 0.015, bz);
        m.rotation.x += 0.01; m.rotation.y += 0.013;
      } else {        // 포물선 토스
        var q = (p - 0.32) / 0.68;
        var arc = 4 * q * (1 - q);
        m.position.set(
          bx + f.drift * q * amp,
          pan.position.y + 0.1 + arc * f.h * amp,
          bz + f.drift * 0.6 * q * amp
        );
        m.rotation.x += f.spin.x * 0.016;
        m.rotation.y += f.spin.y * 0.016;
        m.rotation.z += f.spin.z * 0.016;
      }
    }

    /* 불빛 플리커 + 글로우 */
    flame.intensity = calm ? 1.5 + r * 0.9 : 1.35 + Math.sin(t * 11) * 0.25 + Math.sin(t * 23.7) * 0.18 + r * 0.9;
    glow.material.opacity = calm ? 0.32 + r * 0.15 : 0.28 + Math.abs(Math.sin(t * 7)) * 0.1 + r * 0.15;

    /* 스팀 */
    for (var j = 0; j < steams.length; j++) {
      if (calm) { steams[j].sp.material.opacity = 0; continue; }
      var st = steams[j];
      st.t += st.speed * 0.016;
      if (st.t > 1) { st.t = 0; st.x = (Math.random() - 0.5) * 1.2; st.z = (Math.random() - 0.5) * 1.2; }
      var y = 0.5 + st.t * 2.1;
      st.sp.position.set(st.x + Math.sin(st.t * 6 + j) * 0.12, y, st.z);
      st.sp.scale.setScalar(0.25 + st.t * 0.75);
      st.sp.material.opacity = Math.sin(st.t * Math.PI) * 0.16;
    }

    /* 카메라 스크럽 (감쇠 추적) */
    camAt(r, camTarget);
    var d = 0.09;
    for (var k = 0; k < 3; k++) {
      camNow.pos[k] += (camTarget.pos[k] - camNow.pos[k]) * d;
      camNow.look[k] += (camTarget.look[k] - camNow.look[k]) * d;
    }
    camNow.fov += (camTarget.fov - camNow.fov) * d;
    camera.position.set(camNow.pos[0], camNow.pos[1], camNow.pos[2]);
    camera.lookAt(camNow.look[0], camNow.look[1], camNow.look[2]);
    if (Math.abs(camera.fov - camNow.fov) > 0.05) { camera.fov = camNow.fov; camera.updateProjectionMatrix(); }

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

    renderer.render(scene, camera);
  }
  readScroll();
  frame();
})();
