/* GRIND. Glass refraction: EXPERIMENTAL and OFF by default (add data-refract to an element to try it).
   In testing, Chromium backdrop-filter SVG displacement left seams on some layouts, so the frosted CSS is the shipped look.
   Original note: progressive enhancement. Chromium supports SVG filters in backdrop-filter, so there the
   glass also bends what is behind it at the edges, with a faint colour split. Other browsers keep the CSS frost.
   Refraction profile adapted from liquid-glass-js by Armagan Amcalar (MIT). Usage: <script src="grind-glass.js" defer></script> */
(function () {
  const ok = /Chrome\//.test(navigator.userAgent) && !/Edg\/1[0-1]\d\./.test(navigator.userAgent) && CSS.supports("backdrop-filter", "blur(1px)");
  if (!ok) return;
  const NS = "http://www.w3.org/2000/svg", svg = document.createElementNS(NS, "svg");
  svg.setAttribute("width", "0"); svg.setAttribute("height", "0"); svg.style.position = "absolute";
  document.body.appendChild(svg);
  let n = 0;
  const map = (w, h, r, bend) => {
    const c = document.createElement("canvas"); c.width = w; c.height = h;
    const ctx = c.getContext("2d"), img = ctx.createImageData(w, h), cx = w / 2, cy = h / 2, k = bend * 1920 * Math.min(1, w / 900), M = 400;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const qx = Math.abs(x + .5 - cx) - (cx - r), qy = Math.abs(y + .5 - cy) - (cy - r);
      const d = Math.max(-(Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - r), 0);
      const nx = (x + .5 - cx) / cx, ny = (y + .5 - cy) / cy, len = Math.hypot(nx, ny) || 1;
      const edge = k * (.045 * Math.exp(-.05 * d) + .06 * Math.exp(-.35 * d)), mid = k * .012 * (1 - Math.exp(-.1 * d));
      const i = (y * w + x) * 4;
      img.data[i] = 255 * Math.min(1, Math.max(0, .5 + ((edge * nx) / len + mid * nx) / M));
      img.data[i + 1] = 255 * Math.min(1, Math.max(0, .5 + ((edge * ny) / len + mid * ny) / M));
      img.data[i + 2] = 128; img.data[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0); return c.toDataURL();
  };
  const apply = (el) => {
    const r = el.getBoundingClientRect(); if (r.width < 4 || r.height < 4) return;
    const w = Math.round(r.width), h = Math.round(r.height), cs = getComputedStyle(el);
    const rad = Math.min(parseFloat(cs.borderTopLeftRadius) || 28, h / 2, w / 2);
    const variant = el.dataset.variant || "ink", blur = variant === "lens" ? 0 : variant === "frost" ? 12 : 8;
    const bend = parseFloat(el.dataset.bend || (variant === "lens" ? .3 : 1));
    const id = "grind-glass-" + (n++);
    const f = document.createElementNS(NS, "filter");
    f.setAttribute("id", id); f.setAttribute("x", "0"); f.setAttribute("y", "0"); f.setAttribute("width", w); f.setAttribute("height", h);
    f.setAttribute("filterUnits", "userSpaceOnUse"); f.setAttribute("color-interpolation-filters", "sRGB");
    f.innerHTML = `<feImage href="${map(w, h, rad, bend)}" x="0" y="0" width="${w}" height="${h}" preserveAspectRatio="none" result="m"/>
      <feGaussianBlur in="SourceGraphic" stdDeviation="${blur}" result="b"/>
      ${[1, .96, .92].map((s, i) => `<feDisplacementMap in="b" in2="m" scale="${400 * s}" xChannelSelector="R" yChannelSelector="G" result="d${i}"/>`).join("")}
      <feColorMatrix in="d0" type="matrix" values="1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0" result="r"/>
      <feColorMatrix in="d1" type="matrix" values="0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 0" result="g"/>
      <feColorMatrix in="d2" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 0" result="bl"/>
      <feComposite in="r" in2="g" operator="arithmetic" k2="1" k3="1" result="rg"/><feComposite in="rg" in2="bl" operator="arithmetic" k2="1" k3="1"/>`;
    const old = el.dataset.ggFilter && svg.querySelector("#" + el.dataset.ggFilter); if (old) old.remove();
    svg.appendChild(f); el.dataset.ggFilter = id;
    el.style.backdropFilter = `url(#${id}) saturate(1.25)`;
  };
  const all = () => document.querySelectorAll(".grind-glass[data-refract]").forEach(apply);   // opt-in: data-refract (experimental)
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(all); else all();
  let t; addEventListener("resize", () => { clearTimeout(t); t = setTimeout(all, 150); });
  window.GrindGlass = { refresh: all, apply };
})();
