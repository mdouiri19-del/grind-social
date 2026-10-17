// Grindy, the GRIND. mascot. Reusable three.js character (r169).
// Usage: import { createGrindy, setupStage } from './grindy.js';
//   const g = createGrindy(THREE, RoundedBoxGeometry); scene.add(g.root);
//   g.pose({ expression:'happy', armL:0.9, armR:-0.4, tilt:0, bounce:0, squash:1, glow:0.6, look:[0,0], blink:0, props:{glasses:false,cap:false} });
// Expressions: happy, alert, focused, sleepy, proud, shocked.
// All motion must be driven by a time value t so renders are deterministic (no clocks, no randomness).

export const PALETTE = { lime: '#BFEA4E', green: '#254D3B', ink: '#1B3127', cream: '#F6F7F1', blush: '#F2C6D5', sage: '#E8EFDF', soft: '#80A258' };

export function vinyl(THREE, c, extra = {}) {
  return new THREE.MeshPhysicalMaterial({ color: c, roughness: 0.32, clearcoat: 0.9, clearcoatRoughness: 0.15, ...extra });
}

export function setupStage(THREE, RoomEnvironment, renderer, opts = {}) {
  const bg = opts.background || PALETTE.sage;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 0.88;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const scene = new THREE.Scene();
  scene.background = opts.transparent ? null : new THREE.Color(bg);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.6;
  scene.add(new THREE.HemisphereLight('#ffffff', '#c9d4bd', 0.6));
  const key = new THREE.DirectionalLight('#ffffff', 2.2);
  key.position.set(4, 7, 6); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 8;
  Object.assign(key.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6 });
  scene.add(key);
  const rim = new THREE.DirectionalLight(PALETTE.lime, 0.8); rim.position.set(-5, 3, -4); scene.add(rim);
  if (!opts.noFloor) {
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60),
      opts.transparent ? new THREE.ShadowMaterial({ opacity: 0.2 }) : new THREE.MeshStandardMaterial({ color: bg, roughness: 1 }));
    floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
  }
  return scene;
}

export function createGrindy(THREE, RoundedBoxGeometry) {
  const C = PALETTE;
  const V = (c, e) => vinyl(THREE, c, e);
  const sph = (r, s = 48) => new THREE.SphereGeometry(r, s, s);
  const mk = (g, m, parent, p = [0, 0, 0], r = [0, 0, 0], s = [1, 1, 1]) => {
    const o = new THREE.Mesh(g, m); o.position.set(...p); o.rotation.set(...r); o.scale.set(...s);
    o.castShadow = true; o.receiveShadow = true; parent.add(o); return o;
  };
  const tube = (pts, r, mat, parent) => {
    const curve = new THREE.QuadraticBezierCurve3(...pts.map(p => new THREE.Vector3(...p)));
    const g = new THREE.Group(); parent.add(g);
    mk(new THREE.TubeGeometry(curve, 32, r, 12, false), mat, g);
    mk(sph(r), mat, g, pts[0]); mk(sph(r), mat, g, pts[2]);
    return g;
  };

  const root = new THREE.Group();
  const body = new THREE.Group(); body.position.y = 0.45; root.add(body);   // bounce/squash pivot at feet
  const torso = new THREE.Group(); torso.position.y = 1.75; body.add(torso); // tilt pivot at center

  const mGreen = V(C.green), mInk = V(C.ink);
  mk(new RoundedBoxGeometry(2.3, 2.6, 1.8, 8, 0.55), mGreen, torso);
  const visorMat = V(C.cream, { roughness: 0.2 });
  const visor = mk(new RoundedBoxGeometry(1.75, 0.95, 0.3, 8, 0.45), visorMat, torso, [0, 0.4, 0.85]);

  // eyes: group per eye so we can squash for blink / expression
  const eyeGroups = [];
  const pupils = [];
  for (const sx of [-1, 1]) {
    const eg = new THREE.Group(); eg.position.set(sx * 0.42, 0.4, 1.0); torso.add(eg);
    mk(sph(0.2), V(C.ink, { roughness: 0.15 }), eg, [0, 0, 0], [0, 0, 0], [1, 1.25, 0.6]);
    const hl = mk(sph(0.065), new THREE.MeshBasicMaterial({ color: '#fff' }), eg, [0.07, 0.09, 0.11]);
    eyeGroups.push(eg); pupils.push(hl);
  }
  // brows (used for focused / alert)
  const brows = [-1, 1].map(sx => mk(new RoundedBoxGeometry(0.34, 0.07, 0.06, 2, 0.03), mInk, torso, [sx * 0.42, 0.78, 0.98]));

  // mouths (toggle visibility)
  const mLime = V(C.lime);
  const mouths = {
    smile: tube([[-0.3, 0, 0], [0, -0.24, 0.05], [0.3, 0, 0]], 0.08, mLime, torso),
    grin: tube([[-0.38, 0.04, 0], [0, -0.36, 0.06], [0.38, 0.04, 0]], 0.1, mLime, torso),
    flat: tube([[-0.24, 0, 0], [0, 0, 0.03], [0.24, 0, 0]], 0.07, mLime, torso),
    frown: tube([[-0.26, -0.08, 0], [0, 0.14, 0.04], [0.26, -0.08, 0]], 0.07, mLime, torso),
  };
  const oMouth = mk(sph(0.17), mLime, torso, [0, -0.5, 0.92], [0, 0, 0], [1, 1.25, 0.5]);
  for (const m of Object.values(mouths)) m.position.set(0, -0.5, 0.92);
  mouths.o = oMouth;

  // cheeks
  const cheeks = [-1, 1].map(sx => mk(sph(0.17), V(C.blush, { roughness: 0.6, clearcoat: 0.2 }), torso, [sx * 0.95, -0.2, 0.9], [0, 0, 0], [1, 0.6, 0.3]));

  // antenna
  const antenna = new THREE.Group(); antenna.position.set(0, 1.3, 0); torso.add(antenna);
  mk(new THREE.CapsuleGeometry(0.06, 0.5, 8, 16), mInk, antenna, [0, 0.25, 0]);
  const bulbMat = V(C.lime, { emissive: new THREE.Color('#9CC94A'), emissiveIntensity: 0.5 });
  const bulb = mk(sph(0.22), bulbMat, antenna, [0, 0.65, 0]);

  // arms: pivot at shoulder
  const arm = (sx) => {
    const piv = new THREE.Group(); piv.position.set(sx * 1.15, 0.05, 0.2); torso.add(piv);
    mk(new THREE.CapsuleGeometry(0.15, 0.85, 8, 16), mGreen, piv, [sx * 0.15, -0.5, 0]);
    mk(sph(0.23), mGreen, piv, [sx * 0.22, -1.0, 0]);
    return piv;
  };
  const armL = arm(-1), armR = arm(1);
  // legs
  for (const sx of [-1, 1]) {
    mk(new THREE.CapsuleGeometry(0.17, 0.55, 8, 16), mInk, body, [sx * 0.55, 0.2, 0]);
    mk(sph(0.27), mInk, body, [sx * 0.6, -0.15, 0.15], [0, 0, 0], [1, 0.8, 1.2]);
  }

  // props
  const glasses = new THREE.Group(); torso.add(glasses); glasses.position.set(0, 0.4, 1.06);
  for (const sx of [-1, 1]) mk(new THREE.TorusGeometry(0.26, 0.04, 12, 32), mInk, glasses, [sx * 0.42, 0, 0]);
  mk(new THREE.CapsuleGeometry(0.03, 0.2, 4, 8), mInk, glasses, [0, 0.02, 0], [0, 0, Math.PI / 2]);
  const cap = new THREE.Group(); cap.position.set(0, 1.42, 0); torso.add(cap);
  mk(new RoundedBoxGeometry(2.2, 0.12, 2.2, 2, 0.04), mInk, cap, [0, 0.25, 0], [0, Math.PI / 4, 0]);
  mk(new THREE.CylinderGeometry(0.75, 0.85, 0.35, 32), mInk, cap, [0, 0.05, 0]);
  mk(new THREE.CapsuleGeometry(0.04, 0.6, 4, 8), mLime, cap, [0.85, 0.0, 0.3], [0.2, 0, 0.1]);
  const coffee = new THREE.Group(); armR.add(coffee); coffee.position.set(0.3, -1.25, 0.15);
  mk(new THREE.CylinderGeometry(0.22, 0.17, 0.5, 24), V(C.cream), coffee);
  mk(new THREE.CylinderGeometry(0.235, 0.235, 0.18, 24), V(C.soft), coffee, [0, -0.02, 0]);
  const zzz = new THREE.Group(); torso.add(zzz); zzz.position.set(1.0, 1.6, 0.4);

  const EXPR = {
    happy:   { mouth: 'smile', eyeY: 1, brow: null, visor: C.cream, glow: 0.5, cheeks: true },
    proud:   { mouth: 'grin', eyeY: 0.55, brow: null, visor: C.cream, glow: 0.9, cheeks: true },
    alert:   { mouth: 'o', eyeY: 1.25, brow: 'up', visor: C.blush, glow: 1.6, cheeks: false },
    shocked: { mouth: 'o', eyeY: 1.35, brow: 'up', visor: C.cream, glow: 1.2, cheeks: false },
    focused: { mouth: 'flat', eyeY: 0.6, brow: 'down', visor: C.cream, glow: 0.4, cheeks: false },
    sleepy:  { mouth: 'flat', eyeY: 0.12, brow: null, visor: '#DDE6D2', glow: 0.1, cheeks: true },
    sad:     { mouth: 'frown', eyeY: 0.9, brow: 'sad', visor: C.cream, glow: 0.2, cheeks: false },
  };

  function pose(p = {}) {
    const e = EXPR[p.expression || 'happy'];
    for (const [k, m] of Object.entries(mouths)) m.visible = (k === e.mouth);
    const blink = p.blink || 0; // 0 open, 1 closed
    for (const eg of eyeGroups) eg.scale.y = Math.max(0.08, e.eyeY * (1 - blink));
    for (const h of pupils) h.visible = e.eyeY * (1 - blink) > 0.3;
    const lk = p.look || [0, 0];
    eyeGroups.forEach((eg, i) => { eg.position.x = (i ? 0.42 : -0.42) + lk[0] * 0.12; eg.position.y = 0.4 + lk[1] * 0.08; });
    brows.forEach((b, i) => {
      const s = i ? 1 : -1;
      b.visible = !!e.brow;
      b.position.y = e.brow === 'up' ? 0.86 : e.brow === 'sad' ? 0.74 : 0.7;
      b.rotation.z = e.brow === 'down' ? s * -0.35 : e.brow === 'sad' ? s * 0.35 : 0;
    });
    visorMat.color.set(p.visor || e.visor);
    bulbMat.emissiveIntensity = p.glow ?? e.glow;
    cheeks.forEach(c => c.visible = e.cheeks);
    armL.rotation.z = -(p.armL ?? 0.25);   // positive raises left arm
    armR.rotation.z = (p.armR ?? 0.25);    // positive raises right arm
    armL.rotation.x = p.armLx || 0; armR.rotation.x = p.armRx || 0;
    torso.rotation.z = p.tilt || 0;
    torso.rotation.y = p.turn || 0;
    antenna.rotation.z = p.antenna || 0;
    body.position.y = 0.45 + (p.bounce || 0);
    const sq = p.squash ?? 1; body.scale.set(1 / Math.sqrt(sq), sq, 1 / Math.sqrt(sq));
    const pr = p.props || {};
    glasses.visible = !!pr.glasses; cap.visible = !!pr.cap; coffee.visible = !!pr.coffee;
    root.rotation.y = p.yaw ?? root.rotation.y;
  }
  pose({});
  return { root, pose, parts: { body, torso, armL, armR, antenna, bulb, visor } };
}
