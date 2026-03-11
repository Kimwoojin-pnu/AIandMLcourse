/**
 * PNU Physics - Particle Canvas Animation
 * 물리학 테마의 파티클 + 연결선 애니메이션
 */

(function () {
  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let W, H, particles, mouse;

  const CONFIG = {
    count: 120,
    maxRadius: 2.5,
    minRadius: 0.5,
    speed: 0.4,
    connectDistance: 130,
    colors: ['#3b82f6', '#7c3aed', '#60a5fa', '#a78bfa', '#f59e0b', '#ffffff'],
    mouseRadius: 150,
  };

  function resize() {
    W = canvas.width = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }

  function randBetween(a, b) {
    return a + Math.random() * (b - a);
  }

  function createParticle() {
    return {
      x: Math.random() * W,
      y: Math.random() * H,
      vx: randBetween(-CONFIG.speed, CONFIG.speed),
      vy: randBetween(-CONFIG.speed, CONFIG.speed),
      r: randBetween(CONFIG.minRadius, CONFIG.maxRadius),
      color: CONFIG.colors[Math.floor(Math.random() * CONFIG.colors.length)],
      alpha: randBetween(0.3, 0.9),
      pulse: Math.random() * Math.PI * 2,
      pulseSpeed: randBetween(0.02, 0.05),
    };
  }

  function init() {
    resize();
    particles = Array.from({ length: CONFIG.count }, createParticle);
    mouse = { x: -9999, y: -9999 };

    window.addEventListener('resize', () => {
      resize();
    });

    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    });

    canvas.addEventListener('mouseleave', () => {
      mouse.x = -9999;
      mouse.y = -9999;
    });
  }

  function drawParticle(p) {
    p.pulse += p.pulseSpeed;
    const pulseFactor = 1 + Math.sin(p.pulse) * 0.3;
    const r = p.r * pulseFactor;

    // Glow
    const grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r * 4);
    grd.addColorStop(0, p.color.replace(')', `, ${p.alpha})`).replace('rgb', 'rgba').replace('#', 'rgba(').replace(')', ''));
    grd.addColorStop(1, 'rgba(0,0,0,0)');

    ctx.beginPath();
    ctx.arc(p.x, p.y, r * 4, 0, Math.PI * 2);
    ctx.fillStyle = grd;
    ctx.fill();

    // Core dot
    ctx.beginPath();
    ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.globalAlpha = p.alpha;
    ctx.fill();
    ctx.globalAlpha = 1;
  }

  function connectParticles() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < CONFIG.connectDistance) {
          const alpha = (1 - dist / CONFIG.connectDistance) * 0.4;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(96, 165, 250, ${alpha})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  function updateParticle(p) {
    // Mouse repulsion
    const dx = p.x - mouse.x;
    const dy = p.y - mouse.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < CONFIG.mouseRadius) {
      const force = (CONFIG.mouseRadius - dist) / CONFIG.mouseRadius;
      p.vx += (dx / dist) * force * 0.5;
      p.vy += (dy / dist) * force * 0.5;
    }

    // Velocity damping
    p.vx *= 0.99;
    p.vy *= 0.99;

    // Speed limit
    const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
    if (speed > CONFIG.speed * 3) {
      p.vx = (p.vx / speed) * CONFIG.speed * 3;
      p.vy = (p.vy / speed) * CONFIG.speed * 3;
    }

    p.x += p.vx;
    p.y += p.vy;

    // Wrap around
    if (p.x < -10) p.x = W + 10;
    if (p.x > W + 10) p.x = -10;
    if (p.y < -10) p.y = H + 10;
    if (p.y > H + 10) p.y = -10;
  }

  // Star background
  const stars = Array.from({ length: 200 }, () => ({
    x: Math.random(),
    y: Math.random(),
    r: Math.random() * 1.2 + 0.2,
    alpha: Math.random() * 0.6 + 0.2,
    twinkle: Math.random() * Math.PI * 2,
    twinkleSpeed: Math.random() * 0.02 + 0.005,
  }));

  function drawStars() {
    stars.forEach((s) => {
      s.twinkle += s.twinkleSpeed;
      const a = s.alpha * (0.6 + Math.sin(s.twinkle) * 0.4);
      ctx.beginPath();
      ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 255, 255, ${a})`;
      ctx.fill();
    });
  }

  function animate() {
    ctx.clearRect(0, 0, W, H);

    // Deep space gradient background
    const bgGrd = ctx.createRadialGradient(W / 2, H / 2, 0, W / 2, H / 2, Math.max(W, H));
    bgGrd.addColorStop(0, 'rgba(15, 21, 53, 0.3)');
    bgGrd.addColorStop(0.5, 'rgba(10, 14, 39, 0.2)');
    bgGrd.addColorStop(1, 'rgba(4, 8, 24, 0.1)');
    ctx.fillStyle = bgGrd;
    ctx.fillRect(0, 0, W, H);

    drawStars();
    connectParticles();
    particles.forEach((p) => {
      updateParticle(p);
      drawParticle(p);
    });

    requestAnimationFrame(animate);
  }

  init();
  animate();
})();
