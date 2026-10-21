/* GRIND. signature effects (GX). Plain JS, no footage, deterministic: every frame is a pure function of t.
 * Load after gsap.js. Works in HyperFrames (GX.attach(tl, duration)) and in Grindy three.js pages (call GX.render(t) in renderAt).
 *
 *   GX.screenPush({...})     LCD macro: the hook text on real-looking screen pixels, hard cut word by word.
 *   GX.shoulderZoom({...})   camera pushes in on a subject, card lands on one side, whip pan to a card on the other side
 *                            (style "transition": the first big text breaks into light and streaks into the second card).
 *   GX.glassGraph({...})     liquid glass card over the live scene (frosted + lens-bent refraction), a line draws on a
 *                            velocity ramp, the counter counts with it, punch, hold, sink.
 *
 * Adapted from the "Effect of the Day" Remotion recipes (screen push, over-the-shoulder zoom, liquid glass velocity graph).
 * The glass refraction profile follows liquid-glass-js by Armagan Amcalar (MIT licence). Brand: Inter only, GRIND. palette.
 */
(function () {
  const W = 1080, H = 1920;
  const FX = [];
  const C = { cream: "#F6F7F1", ink: "#203A2D", sec: "#586650", brand: "#254D3B", lime: "#D9F88D", blush: "#F2DEE5" };

  // ---------- helpers
  const clamp01 = (x) => Math.max(0, Math.min(1, x));
  const bezier = (x1, y1, x2, y2) => (x) => {           // cubic-bezier easing, solved by bisection
    if (x <= 0) return 0; if (x >= 1) return 1;
    let lo = 0, hi = 1, u = x;
    for (let i = 0; i < 30; i++) {
      u = (lo + hi) / 2;
      const bx = 3 * (1 - u) * (1 - u) * u * x1 + 3 * (1 - u) * u * u * x2 + u * u * u;
      if (bx < x) lo = u; else hi = u;
    }
    return 3 * (1 - u) * (1 - u) * u * y1 + 3 * (1 - u) * u * u * y2 + u * u * u;
  };
  const lerpT = (t, a, b, from, to, ease) => from + (to - from) * (ease || ((x) => x))(clamp01((t - a) / (b - a)));
  const keys3 = (t, a, b, c, ease) => (t <= a || t >= c) ? 0 : t < b ? ease((t - a) / (b - a)) : 1 - ease((t - b) / (c - b));
  const rand = (s) => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return ((h >>> 0) % 100000) / 100000; };
  // damped spring 0 -> 1 (stiffness 170, damping 12, mass 0.7), closed form
  const spring = (s) => {
    if (s <= 0) return 0;
    const w0 = Math.sqrt(170 / 0.7), z = 12 / (2 * Math.sqrt(170 * 0.7)), wd = w0 * Math.sqrt(1 - z * z);
    return 1 - Math.exp(-z * w0 * s) * (Math.cos(wd * s) + (z * w0 / wd) * Math.sin(wd * s));
  };
  const el = (tag, css, parent, html) => { const e = document.createElement(tag); if (css) e.style.cssText = css; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e; };
  const rgb = (hex) => { const n = parseInt(hex.replace("#", ""), 16); return `${(n >> 16) & 255},${(n >> 8) & 255},${n & 255}`; };
  const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[c]);
  const rootOf = (o) => (typeof o.root === "string" ? document.querySelector(o.root) : o.root) || document.getElementById("root") || document.body;
  const FONT_Q = ["700 150px Inter", "700 64px Inter", "600 30px Inter"];
  if (document.fonts) FONT_Q.forEach((f) => document.fonts.load(f));
  const fontsReady = () => !document.fonts || FONT_Q.every((f) => document.fonts.check(f));

  // ================================================================== 1. SCREEN PUSH
  GX_screenPush.defaults = { drift: 0.07, zIndex: 40, color: C.lime, screen: "#1E2B24", zoom: 3.1, pixel: 10, fringe: 3, glow: 0.85, focus: 5 };
  function GX_screenPush(opts) {
    const o = Object.assign({}, GX_screenPush.defaults, opts);
    const SIZE = 150, PAD = 1400, ROWX = 1200, P = o.pixel, k = P / 10;
    const SUB = [["#ff8a7a", 2], ["#9affb0", 6], ["#8aa8ff", 10]].map(([c, x]) =>
      `radial-gradient(ellipse ${1.7 * k}px ${4.3 * k}px at ${x * k}px ${5.5 * k}px, ${c} 70%, transparent 100%)`).join(", ");
    const root = rootOf(o);
    const layer = el("div", `position:absolute;inset:0;overflow:hidden;background:${o.screen};display:none;z-index:${o.zIndex}`, root);
    const cam = el("div", "position:absolute;left:540px;top:960px;transform-origin:0 0", layer);
    const rowCss = (color, dx) => `position:absolute;left:${ROWX + dx}px;top:${PAD - SIZE * 0.82}px;font-family:Inter,sans-serif;font-weight:700;font-size:${SIZE}px;line-height:1;letter-spacing:${-0.01 * SIZE}px;white-space:pre;color:${color}`;
    const rowHtml = o.words.map((w) => `<span>${esc(w.text)}</span>`).join(" ");
    const makePlane = (parent, extra) => {
      const plane = el("div", `position:absolute;top:0;height:${2 * PAD}px;background:${o.screen};isolation:isolate;overflow:hidden`, parent);
      const inner = el("div", "position:absolute;left:0;top:0", plane);
      el("div", rowCss("#ff3020", -o.fringe) + ";mix-blend-mode:screen", inner, rowHtml);
      el("div", rowCss("#20d8ff", o.fringe) + ";mix-blend-mode:screen", inner, rowHtml);
      const main = el("div", rowCss(o.color, 0), inner, rowHtml);
      el("div", `position:absolute;inset:0;mix-blend-mode:multiply;background-color:#000;background-image:${SUB};background-size:${P}px ${P}px`, plane);
      return { plane, inner, main };
    };
    const A = makePlane(cam);
    const glowWrap = el("div", `position:absolute;left:0;top:0;mix-blend-mode:screen;filter:blur(4px) brightness(1.6);opacity:${o.glow}`, cam);
    const B = makePlane(glowWrap);
    if (o.focus > 0) el("div", `position:absolute;inset:0;backdrop-filter:blur(${o.focus}px);-webkit-backdrop-filter:blur(${o.focus}px);-webkit-mask-image:linear-gradient(180deg,#000 0%,transparent 34%,transparent 66%,#000 100%);mask-image:linear-gradient(180deg,#000 0%,transparent 34%,transparent 66%,#000 100%)`, layer);
    let placed = null, measuredReady = false;
    const measure = () => { measuredReady = fontsReady(); const sp = A.main.querySelectorAll("span"); placed = o.words.map((w, i) => ({ t: w.t, x: ROWX + sp[i].offsetLeft, w: sp[i].offsetWidth })); };
    FX.push((t) => {
      const on = t >= o.words[0].t && t < o.end;
      layer.style.display = on ? "block" : "none";
      if (!on) return;
      if (!placed || !measuredReady) measure();
      let i = 0; while (i < placed.length - 1 && t >= placed[i + 1].t) i++;
      const cur = placed[i];
      const jx = ((i * 37) % 11) - 5, jy = ((i * 23) % 9) - 4;
      const cx = cur.x + cur.w / 2 + jx, cy = PAD - SIZE * 0.36 + jy;
      const z = Math.min(o.zoom, (0.84 * W) / Math.max(cur.w, 1));
      const half = W / 2 / z + 4 * P, L = Math.floor((cx - half) / P) * P, span = Math.ceil((2 * half) / P + 2) * P;
      for (const pl of [A, B]) { pl.plane.style.left = L + "px"; pl.plane.style.width = span + "px"; pl.inner.style.left = -L + "px"; }
      // inside each word the camera keeps creeping in (no slide between words: every new word is still a hard cut)
      const nextT = i < placed.length - 1 ? placed[i + 1].t : o.end, u = clamp01((t - cur.t) / Math.max(0.05, nextT - cur.t));
      const zz = z * (1 + o.drift * (1 - Math.pow(1 - u, 2)));
      cam.style.transform = `scale(${zz}) translate(${-cx}px, ${-cy}px)`;
      layer.style.filter = t - cur.t < 0.05 ? "brightness(1.35)" : "none";   // a one-frame flash on every cut
    });
  }

  // ================================================================== 2. OVER-THE-SHOULDER ZOOM
  GX_shoulderZoom.defaults = { zIndex: 30, style: "normal", accent: C.brand, cardTop: 600, anchorY: 0.42 };
  function GX_shoulderZoom(opts) {
    const o = Object.assign({}, GX_shoulderZoom.defaults, opts);
    const T0 = o.at, root = rootOf(o);
    const camEl = typeof o.camera === "string" ? document.querySelector(o.camera) : o.camera;
    const CURVES = { in: [0, 0.21, 0.43, 0.61, 0.73, 0.83, 0.9, 0.96, 1], out: [0, 0.14, 0.37, 0.57, 0.71, 0.8, 0.87, 0.94, 1] };
    const CURVE_OF = { in: "in", pan: "in", whip: "in", drift: "out", return: "out" };
    const DUR_OF = { in: 0.36, pan: 0.42, whip: 0.5, drift: 0.42, return: 0.9 };
    const prog = (kind, u) => {
      if (u <= 0) return 0; if (u >= 1) return 1;
      const p = CURVES[CURVE_OF[kind]], x = u * (p.length - 1), i = Math.floor(x), f = x - i, n = p.length - 1;
      const m = (j) => (p[Math.min(j + 1, n)] - p[Math.max(j - 1, 0)]) / (Math.min(j + 1, n) - Math.max(j - 1, 0));
      return (2 * f ** 3 - 3 * f ** 2 + 1) * p[i] + (f ** 3 - 2 * f ** 2 + f) * m(i) + (-2 * f ** 3 + 3 * f ** 2) * p[i + 1] + (f ** 3 - f ** 2) * m(i + 1);
    };
    const MOVES = [
      { t: T0 + 0.05, kind: "in", to: 1.25, dur: 0.5 }, { t: T0 + 0.9, kind: "pan", to: 1.25, x: 110 },
      { t: T0 + 2.4, kind: "whip", to: 1.27, x: -110 }, { t: T0 + 2.9, kind: "drift", to: 1.25, dur: 0.2 },
      { t: T0 + 3.7, kind: "return", to: 1.0, x: 0 }];
    const camAt = (t) => {
      let z = 1, x = 0;
      for (const m of MOVES) {
        if (t < m.t) break;
        const d = m.dur || DUR_OF[m.kind], u = (t - m.t) / d, p = prog(m.kind, u), fz = z, fx = x;
        z = Math.exp(Math.log(fz) + (Math.log(m.to) - Math.log(fz)) * p);
        if (m.x !== undefined) x = fx + (m.x - fx) * p;
        if (u >= 1) { z = m.to; if (m.x !== undefined) x = m.x; }
      }
      return { z, x };
    };
    if (camEl) camEl.style.transformOrigin = `540px ${o.anchorY * H}px`;

    const CARD = { top: o.cardTop, edge: 70, w: 330, padX: 30, padY: 26, r: 26 };
    const EYE_H = 30, BIG_H = 80, BIG_BASE = 63, SUB_H = 34, INNER = CARD.w - 2 * CARD.padX - 6, RES = 2;
    const CARD_H = 6 + 2 * CARD.padY + EYE_H + BIG_H + SUB_H;
    const layer = el("div", `position:absolute;inset:0;pointer-events:none;z-index:${o.zIndex}`, root);
    const bigFont = (s) => `700 ${s}px Inter, sans-serif`;
    const drawBig = (ctx, text, color) => {
      ctx.setTransform(RES, 0, 0, RES, 0, 0); ctx.clearRect(0, 0, INNER, BIG_H);
      let s = 64; ctx.font = bigFont(s);
      while (s > 26 && ctx.measureText(text).width > INNER) { s -= 2; ctx.font = bigFont(s); }
      ctx.fillStyle = color; ctx.textBaseline = "alphabetic"; ctx.fillText(text, 0, BIG_BASE);
    };
    const mkCard = (side, card) => {
      const d = el("div", `position:absolute;top:${CARD.top}px;${side === "l" ? "left" : "right"}:${CARD.edge}px;width:${CARD.w}px;padding:${CARD.padY}px ${CARD.padX}px;box-sizing:border-box;border-radius:${CARD.r}px;background:#fff;border:3px solid ${o.accent};opacity:0;display:none`, layer);
      el("div", `height:${EYE_H}px;font-family:Inter,sans-serif;font-weight:600;font-size:22px;letter-spacing:3px;color:${o.accent};white-space:nowrap;overflow:hidden;text-transform:uppercase`, d, esc(card.label || ""));
      const cv = el("canvas", `display:block;width:${INNER}px;height:${BIG_H}px`, d); cv.width = INNER * RES; cv.height = BIG_H * RES;
      el("div", `height:${SUB_H}px;font-family:Inter,sans-serif;font-weight:600;font-size:26px;color:#8A8F86;white-space:nowrap;overflow:hidden`, d, esc(card.small || ""));
      return { d, cv, side, card, drawn: false };
    };
    const L = mkCard("l", o.start), R = mkCard("r", o.end);
    const transition = o.style === "transition";
    const DEPART = T0 + 2.38, CHARGE = DEPART - 0.25;
    let streak = null, ps = null, arrive = T0 + 2.9;
    if (transition) { streak = el("canvas", `position:absolute;left:0;top:0;width:${W}px;height:${H}px`, layer); streak.width = W; streak.height = H; }
    const sample = (text, side) => {
      const c = document.createElement("canvas"); c.width = INNER * RES; c.height = BIG_H * RES;
      const ctx = c.getContext("2d"); drawBig(ctx, text, "#000");
      const d = ctx.getImageData(0, 0, c.width, c.height).data;
      const left = side === "l" ? CARD.edge : W - CARD.edge - CARD.w;
      const cx = left + CARD.w / 2, cy = CARD.top + CARD_H / 2, a = ((side === "l" ? -4 : 4) * Math.PI) / 180, pts = [];
      for (let y = 0; y < c.height; y += 4) for (let x = 0; x < c.width; x += 4) if (d[(y * c.width + x) * 4 + 3] > 110) {
        const lx = left + 3 + CARD.padX + x / RES - cx, ly = CARD.top + 3 + CARD.padY + EYE_H + y / RES - cy;
        pts.push({ x: cx + lx * Math.cos(a) - ly * Math.sin(a), y: cy + lx * Math.sin(a) + ly * Math.cos(a), xn: x / c.width });
      }
      return pts.sort((p, q) => p.x - q.x);
    };
    const warp = (u) => (u <= 0 ? 0 : u >= 1 ? 1 : u < 0.5 ? 0.5 * Math.pow(2, 20 * u - 10) : 1 - 0.5 * Math.pow(2, -20 * u + 10));
    const posAt = (p, t) => {
      const u = clamp01((t - p.dep) / p.fl), e = warp(u), bulge = Math.sin(Math.PI * e);
      let x = p.sx + (p.gx - p.sx) * e, y = p.sy + (p.gy - p.sy) * e + (p.r - 0.5) * 110 * bulge;
      const sh = u <= 0 ? lerpT(t, CHARGE, p.dep, 0, 1, (q) => q * q) : 0, fr = Math.floor(t * 60);
      x += (rand(`x${p.r}${fr}`) - 0.5) * 2.4 * sh; y += (rand(`y${p.r}${fr}`) - 0.5) * 2.4 * sh;
      return { x, y, u, e };
    };
    const build = () => {
      for (const c of [L, R]) { drawBig(c.cv.getContext("2d"), c.card.big || "", c.side === "l" ? C.ink : o.accent); c.drawn = fontsReady(); }
      if (!fontsReady()) return;
      if (transition) {
        const A = sample(o.start.big, "l"), G = sample(o.end.big, "r"), n = Math.max(A.length, G.length); ps = [];
        for (let i = 0; i < n && A.length && G.length; i++) {
          const s = A[Math.floor((i * A.length) / n)], g = G[Math.floor((i * G.length) / n)], r = rand(`p${i}`);
          ps.push({ sx: s.x, sy: s.y, gx: g.x, gy: g.y, r, fl: 0.34 * (0.85 + 0.3 * rand(`q${i}`)), dep: DEPART + 0.1 * (1 - s.xn) + 0.05 * r });
        }
        arrive = ps.reduce((m, p) => Math.max(m, p.dep + p.fl), 0) || T0 + 2.9;
      }
    };
    const showCard = (c, t, at, out, bigVisible, flash) => {
      if (t < at || t > out + 0.25) { c.d.style.display = "none"; return; }
      const p = spring(t - at) * (1 - lerpT(t, out, out + 0.2, 0, 1, bezier(0.16, 1, 0.3, 1)));
      c.d.style.display = "block";
      c.d.style.opacity = Math.min(1, p * 2);
      c.d.style.transform = `scale(${0.6 + 0.4 * p}) rotate(${c.side === "l" ? -4 : 4}deg)`;
      c.d.style.boxShadow = `0 22px 50px rgba(32,58,45,0.22), 0 0 ${34 + 50 * flash}px rgba(${rgb(C.lime)},${0.55 + 0.4 * flash})`;
      c.d.style.filter = flash > 0 ? `brightness(${1 + 0.35 * flash})` : "none";
      c.cv.style.opacity = bigVisible ? 1 : 0;
    };
    FX.push((t) => {
      if (!L.drawn) build();
      const { z, x } = camAt(t);
      if (camEl) camEl.style.transform = `translate(${x}px, 0px) scale(${z})`;
      const flash = transition && t >= arrive ? Math.max(0, 1 - (t - arrive) / 0.2) : 0;
      showCard(L, t, T0 + 1.0, T0 + 2.35, !transition || t < CHARGE, 0);
      showCard(R, t, T0 + (transition ? 2.7 : 2.55), T0 + 3.7, !transition || t >= arrive, flash);
      if (!streak) return;
      const ctx = streak.getContext("2d"); ctx.clearRect(0, 0, W, H);
      if (t < CHARGE || t >= arrive || !ps) return;
      const still = new Path2D(), landed = new Path2D(), glow = new Path2D();
      for (const p of ps) {
        const a = posAt(p, t), b = posAt(p, t - 0.045);
        if (a.u <= 0 || a.e < 0.015) still.rect(a.x - 1.2, a.y - 1.2, 2.4, 2.4);
        else if (a.u >= 1 || a.e > 0.985) landed.rect(a.x - 1.2, a.y - 1.2, 2.4, 2.4);
        else { glow.moveTo(b.x, b.y); glow.lineTo(a.x + 0.01, a.y); }
      }
      const charge = lerpT(t, CHARGE, DEPART, 0, 1, (q) => q * q);
      ctx.fillStyle = C.ink; ctx.shadowColor = o.accent; ctx.shadowBlur = 36 * charge; ctx.fill(still); ctx.shadowBlur = 0;
      ctx.fillStyle = o.accent; ctx.fill(landed);
      ctx.lineCap = "round";
      ctx.strokeStyle = `rgba(${rgb(o.accent)},0.35)`; ctx.lineWidth = 6; ctx.stroke(glow);
      ctx.strokeStyle = `rgba(${rgb(C.lime)},0.95)`; ctx.lineWidth = 2; ctx.stroke(glow);
    });
  }

  // ================================================================== 3. LIQUID GLASS GRAPH
  let glassN = 0;
  GX_glassGraph.defaults = { zIndex: 35, title: "SAMPLE", startValue: 18, endValue: 82, prefix: "", suffix: "%", decimals: 0,
    line: C.lime, node: C.cream, text: C.cream, tint: 0.62, tintColor: C.brand, shape: [0.18, 0.22, 0.26, 0.34, 0.4, 0.52, 0.64, 0.78, 0.92],
    draw: 1.16, hold: 1.5, top: 760, frost: 7, bend: 1.0 };
  function GX_glassGraph(opts) {
    const o = Object.assign({}, GX_glassGraph.defaults, opts);
    const root = rootOf(o), id = `gx-glass-${glassN++}`;
    const CW = 900, HC = 610, R = 34, GRAPH_H = 420, PAD = 40, MAP = 400;
    const T_RISE = 0.22, T_DRAW = 0.18, T_PUNCH = 0.28, T_EXIT = 0.3;
    const source = () => (typeof o.source === "string" ? document.querySelector(o.source) : o.source);
    // refraction map: red = x offset, green = y offset, 128 = none
    const c = document.createElement("canvas"); c.width = CW; c.height = HC;
    const ctx = c.getContext("2d"), img = ctx.createImageData(CW, HC), cx0 = CW / 2, cy0 = HC / 2;
    for (let y = 0; y < HC; y++) for (let x = 0; x < CW; x++) {
      const qx = Math.abs(x + 0.5 - cx0) - (cx0 - R), qy = Math.abs(y + 0.5 - cy0) - (cy0 - R);
      const out = Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - R, d = Math.max(-out, 0);
      const nx = (x + 0.5 - cx0) / cx0, ny = (y + 0.5 - cy0) / cy0, len = Math.hypot(nx, ny) || 1;
      const px = o.bend * 1920 * (0.045 * Math.exp(-0.05 * d) + 0.06 * Math.exp(-0.35 * d) + 0.012 * (1 - Math.exp(-0.1 * d)));
      const i = (y * CW + x) * 4;
      img.data[i] = Math.round(255 * clamp01(0.5 + (px * nx) / len / MAP)); img.data[i + 1] = Math.round(255 * clamp01(0.5 + (px * ny) / len / MAP));
      img.data[i + 2] = 128; img.data[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    const map = c.toDataURL("image/png");
    const NS = "http://www.w3.org/2000/svg";
    const svgWrap = el("div", "position:absolute;width:0;height:0;overflow:hidden", root,
      `<svg width="0" height="0"><filter id="${id}" filterUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}" color-interpolation-filters="sRGB">
        <feImage href="${map}" x="0" y="0" width="${CW}" height="${HC}" preserveAspectRatio="none" result="map"/>
        <feGaussianBlur in="SourceGraphic" stdDeviation="${o.frost}" result="frost"/>
        <feDisplacementMap in="frost" in2="map" scale="${MAP}" xChannelSelector="R" yChannelSelector="G" result="dR"/>
        <feDisplacementMap in="frost" in2="map" scale="${MAP * 0.96}" xChannelSelector="R" yChannelSelector="G" result="dG"/>
        <feDisplacementMap in="frost" in2="map" scale="${MAP * 0.92}" xChannelSelector="R" yChannelSelector="G" result="dB"/>
        <feColorMatrix in="dR" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r"/>
        <feColorMatrix in="dG" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g"/>
        <feColorMatrix in="dB" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b"/>
        <feComposite in="r" in2="g" operator="arithmetic" k2="1" k3="1" result="rg"/>
        <feComposite in="rg" in2="b" operator="arithmetic" k2="1" k3="1"/></filter></svg>`);
    const fe = svgWrap.querySelector("feImage"), dms = svgWrap.querySelectorAll("feDisplacementMap");
    const refr = el("div", `position:absolute;inset:0;display:none;z-index:${o.zIndex}`, root);
    const refrIn = el("div", `position:absolute;inset:0;filter:url(#${id})`, refr);
    const card = el("div", `position:absolute;left:${(W - CW) / 2}px;top:${o.top}px;width:${CW}px;height:${HC}px;border-radius:${R}px;display:none;z-index:${o.zIndex + 1};transform-origin:50% 50%;
      background:linear-gradient(180deg, rgba(${rgb(o.tintColor)},${o.tint}), rgba(${rgb(o.tintColor)},${o.tint * 0.8}) 60%, rgba(${rgb(o.tintColor)},${Math.min(1, o.tint * 1.2)}));box-shadow:0 30px 70px rgba(32,58,45,0.35)`, root);
    el("div", `position:absolute;inset:0;border-radius:${R}px;padding:2px;background:linear-gradient(140deg, rgba(255,255,255,0.8), rgba(255,255,255,0.12) 32%, rgba(255,255,255,0.05) 62%, rgba(255,255,255,0.4));-webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude`, card);
    el("div", `position:absolute;inset:0;border-radius:${R}px;background:radial-gradient(120% 70% at 12% -10%, rgba(255,255,255,0.22), rgba(255,255,255,0) 50%);box-shadow:inset 0 1.5px 1px rgba(255,255,255,0.45), inset 0 -18px 40px rgba(255,255,255,0.05)`, card);
    const body = el("div", "position:relative;padding:34px 0 0", card);
    const head = el("div", "display:flex;justify-content:space-between;align-items:baseline;padding:0 40px 18px", body);
    el("span", `font-family:Inter,sans-serif;font-weight:600;font-size:30px;letter-spacing:4px;color:rgba(${rgb(o.text)},0.85)`, head, esc(o.title));
    const num = el("span", `font-family:Inter,sans-serif;font-weight:700;font-size:84px;letter-spacing:-2px;color:${o.text};font-variant-numeric:tabular-nums`, head);
    const svg = document.createElementNS(NS, "svg"); svg.setAttribute("width", CW); svg.setAttribute("height", GRAPH_H); svg.style.cssText = "display:block;overflow:visible"; body.appendChild(svg);
    svg.innerHTML = `<defs><linearGradient id="${id}-f" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${o.line}" stop-opacity="0.45"/><stop offset="1" stop-color="${o.line}" stop-opacity="0"/></linearGradient></defs>` +
      [0.25, 0.5, 0.75].map((g) => `<line x1="${PAD}" x2="${CW - PAD}" y1="${g * GRAPH_H}" y2="${g * GRAPH_H}" stroke="rgba(${rgb(o.text)},0.12)" stroke-width="2"/>`).join("") +
      `<path class="fill" fill="url(#${id}-f)"/><path class="ln" fill="none" stroke="${o.line}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" style="filter:drop-shadow(0 0 10px rgba(${rgb(o.line)},0.8))"/>` +
      `<circle class="nd" r="13" fill="${o.node}" stroke="${o.line}" stroke-width="6"/>`;
    const pFill = svg.querySelector(".fill"), pLine = svg.querySelector(".ln"), node = svg.querySelector(".nd");
    const pts = o.shape.map((y, i) => [PAD + (i / (o.shape.length - 1)) * (CW - 2 * PAD), (1 - y) * GRAPH_H]);
    const seg = pts.slice(1).map((p, i) => Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1])), total = seg.reduce((a, b) => a + b, 0);
    const fmt = (v) => `${o.prefix}${v.toLocaleString("en-US", { minimumFractionDigits: o.decimals, maximumFractionDigits: o.decimals })}<span style="font-size:46px">${esc(o.suffix)}</span>`;
    const eRise = bezier(0.16, 1, 0.3, 1), eDraw = bezier(0.7, 0, 0.25, 1), ePunch = bezier(0.33, 0, 0.2, 1), eExit = bezier(0.5, 0, 0.9, 0.4);
    FX.push((T) => {
      const t = T - o.at, drawEnd = T_DRAW + o.draw, exitStart = drawEnd + o.hold;
      const rise = lerpT(t, 0, T_RISE, 0, 1, eRise), draw = lerpT(t, T_DRAW, drawEnd, 0, 1, eDraw);
      const punch = t < drawEnd - 0.04 || t > drawEnd + T_PUNCH ? 0 : t < drawEnd + 0.08 ? ePunch((t - drawEnd + 0.04) / 0.12) : 1 - ePunch((t - drawEnd - 0.08) / (T_PUNCH - 0.08));
      const exit = lerpT(t, exitStart, exitStart + T_EXIT, 0, 1, eExit);
      const vis = t >= 0 && exit < 1;
      refr.style.display = card.style.display = vis ? "block" : "none";
      if (!vis) return;
      const s = (0.96 + 0.04 * rise) * (1 + 0.035 * punch), dy = (1 - rise) * 60 + exit * 40, op = rise * (1 - exit);
      const cx = 540, cy = o.top + HC / 2 + dy, rx = cx - (CW * s) / 2, ry = cy - (HC * s) / 2, rw = CW * s, rh = HC * s;
      // refract a fresh copy of the live scene behind the card
      const src = source();
      refrIn.textContent = "";
      if (src) { const cl = src.cloneNode(true); cl.removeAttribute("id"); cl.querySelectorAll("[id]").forEach((n) => n.removeAttribute("id")); cl.style.display = "block"; cl.style.visibility = "visible"; refrIn.appendChild(cl); }
      fe.setAttribute("x", rx); fe.setAttribute("y", ry); fe.setAttribute("width", rw); fe.setAttribute("height", rh);
      dms.forEach((d, i) => d.setAttribute("scale", MAP * s * [1, 0.96, 0.92][i]));
      refr.style.opacity = op;
      refr.style.clipPath = `inset(${ry}px ${W - rx - rw}px ${H - ry - rh}px ${rx}px round ${R * s}px)`;
      card.style.opacity = op; card.style.transform = `translateY(${dy}px) scale(${s})`;
      let left = draw * total, k = 0;
      while (k < seg.length - 1 && left > seg[k]) { left -= seg[k]; k++; }
      const u = seg[k] ? Math.min(1, left / seg[k]) : 0;
      const hd = [pts[k][0] + (pts[k + 1][0] - pts[k][0]) * u, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * u];
      const d = [...pts.slice(0, k + 1), hd].map((p, i) => `${i ? "L" : "M"}${p[0]},${p[1]}`).join(" ");
      pLine.setAttribute("d", d);
      pFill.setAttribute("d", `${d} L${hd[0]},${GRAPH_H} L${PAD},${GRAPH_H} Z`); pFill.setAttribute("opacity", Math.min(1, draw * 4));
      node.setAttribute("cx", hd[0]); node.setAttribute("cy", hd[1]); node.setAttribute("opacity", draw > 0.01 ? 1 : 0);
      num.innerHTML = fmt(o.startValue + (o.endValue - o.startValue) * draw);
    });
  }

  window.GX = {
    screenPush: GX_screenPush, shoulderZoom: GX_shoulderZoom, glassGraph: GX_glassGraph,
    render: (t) => { for (const f of FX) f(t); },
    // HyperFrames: one driver tween over the whole reel, so every effect is redrawn from the timeline's own time on every seek.
    attach: (tl, duration) => { const d = { v: 0 }; tl.fromTo(d, { v: 0 }, { v: 1, duration, ease: "none", immediateRender: false, onUpdate: () => GX.render(tl.time()) }, 0); GX.render(0); },
  };
})();
