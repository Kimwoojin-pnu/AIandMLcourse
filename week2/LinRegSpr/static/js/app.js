/**
 * HooksLawNet — Frontend interactivity
 * Handles: mass slider, live predictions, spring SVG animation, Chart.js charts
 */

"use strict";

// ── DOM refs ─────────────────────────────────────────────────────────────────
const slider       = document.getElementById("mass-slider");
const massDisplay  = document.getElementById("mass-display");
const nnResult     = document.getElementById("nn-result");
const theoResult   = document.getElementById("theo-result");
const errorResult  = document.getElementById("error-result");
const springElongTxt = document.getElementById("spring-elongation");
const loadingSpinner = document.getElementById("loading-spinner");
const resultsPanel   = document.getElementById("results-panel");

// ── Constants ────────────────────────────────────────────────────────────────
const K = 50.0;   // spring constant (matches server)
const G = 9.81;

let debounceTimer;
let lossChart = null;
let maeChart  = null;

// ── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initParticles();
  initSpringHero();
  loadModelInfo();
  loadCharts();
  predict(parseFloat(slider.value));
  syncSliderGradient(slider);
});

// ── Slider ───────────────────────────────────────────────────────────────────
slider.addEventListener("input", (e) => {
  const mass = parseFloat(e.target.value);
  syncSliderGradient(slider);
  massDisplay.textContent = `${mass.toFixed(2)} kg`;
  document.querySelectorAll(".mass-btn").forEach(b =>
    b.classList.toggle("active", parseFloat(b.dataset.mass) === mass)
  );
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => predict(mass), 120);
});

function syncSliderGradient(el) {
  const pct = ((el.value - el.min) / (el.max - el.min)) * 100;
  el.style.setProperty("--pct", `${pct}%`);
}

// ── Quick-mass buttons ────────────────────────────────────────────────────────
window.setMass = function (mass) {
  slider.value = mass;
  syncSliderGradient(slider);
  massDisplay.textContent = `${parseFloat(mass).toFixed(2)} kg`;
  document.querySelectorAll(".mass-btn").forEach(b =>
    b.classList.toggle("active", parseFloat(b.dataset.mass) === mass)
  );
  predict(mass);
};

// ── Predict ───────────────────────────────────────────────────────────────────
async function predict(mass) {
  loadingSpinner.classList.remove("hidden");
  resultsPanel.style.opacity = "0.45";

  try {
    const res  = await fetch("/api/predict", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ mass }),
    });
    if (!res.ok) throw new Error(await res.text());
    const d = await res.json();

    // Update result text
    nnResult.textContent    = `${d.elongation_cm.toFixed(2)} cm`;
    theoResult.textContent  = `${d.theoretical_cm.toFixed(2)} cm`;
    errorResult.textContent = `${d.error_pct.toFixed(3)} %`;
    springElongTxt.textContent = `${d.elongation_cm.toFixed(2)} cm`;

    // Colour-code error
    errorResult.style.color = d.error_pct < 1 ? "#10b981" : d.error_pct < 5 ? "#f97316" : "#ef4444";

    // Animate spring
    updateSpring(d.elongation_m, mass);

    // Slide-in result
    resultsPanel.classList.add("fade-in");
    setTimeout(() => resultsPanel.classList.remove("fade-in"), 700);
  } catch (err) {
    console.error("Predict error:", err);
  } finally {
    loadingSpinner.classList.add("hidden");
    resultsPanel.style.opacity = "1";
  }
}

// ── Spring SVG animation ──────────────────────────────────────────────────────
function updateSpring(elongation_m, mass_kg) {
  const coilsGroup = document.getElementById("spring-coils");
  const massSvgRect = document.getElementById("spring-mass");
  const massLabel   = document.getElementById("mass-label");
  const svgEl       = document.getElementById("spring-svg");

  const svgW   = 100;
  const topY   = 12;           // ceiling bottom
  const coils  = 9;
  const amp    = 22;

  // Scale: 1 m elongation = 130 px
  const visualLen = Math.min(Math.max(elongation_m * 120 + 38, 42), 220);
  const bottomY   = topY + visualLen;

  // Draw spring path
  const pts = [];
  const steps = coils * 36;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = svgW / 2 + amp * Math.sin(2 * Math.PI * coils * t);
    const y = topY + t * visualLen;
    pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  }
  coilsGroup.setAttribute("points", pts.join(" "));

  // Reposition mass box
  const massH = 38;
  massSvgRect.setAttribute("y",      bottomY + 4);
  massSvgRect.setAttribute("x",      svgW / 2 - 28);
  massSvgRect.setAttribute("width",  56);
  massSvgRect.setAttribute("height", massH);

  massLabel.setAttribute("x", svgW / 2);
  massLabel.setAttribute("y", bottomY + 4 + massH / 2 + 5);
  massLabel.textContent = `${parseFloat(mass_kg).toFixed(1)} kg`;

  // Resize SVG
  const totalH = bottomY + massH + 20;
  svgEl.setAttribute("height", Math.max(totalH, 180));
}

// ── Model info ────────────────────────────────────────────────────────────────
async function loadModelInfo() {
  try {
    const res  = await fetch("/api/model-info");
    const info = await res.json();
    setText("stat-params",  (info.model_params || 0).toLocaleString());
    setText("stat-mae",     info.final_mae      ? `${(info.final_mae * 1000).toFixed(3)} mm`  : "—");
    setText("stat-val-mae", info.final_val_mae   ? `${(info.final_val_mae * 1000).toFixed(3)} mm` : "—");
    setText("stat-epochs",  info.epochs_run ?? "—");
    setText("stat-loss",    info.final_loss      ? info.final_loss.toExponential(2) : "—");
  } catch (e) { console.warn("model-info:", e); }
}

// ── Interactive charts (Chart.js) ─────────────────────────────────────────────
async function loadCharts() {
  // Wait for Chart.js to be ready
  if (typeof Chart === "undefined") {
    setTimeout(loadCharts, 300);
    return;
  }
  try {
    const res  = await fetch("/api/history");
    if (!res.ok) return;
    const hist = await res.json();
    const labels = hist.loss.map((_, i) => i + 1);

    Chart.defaults.color          = "#8b949e";
    Chart.defaults.borderColor    = "#21262d";
    Chart.defaults.font.family    = "Inter, sans-serif";
    Chart.defaults.font.size      = 11;

    // ── Loss chart ──
    const lossCtx = document.getElementById("chart-loss")?.getContext("2d");
    if (lossCtx) {
      lossChart = new Chart(lossCtx, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Train Loss",
              data:  hist.loss,
              borderColor:     "#00d4ff",
              backgroundColor: "rgba(0,212,255,.06)",
              borderWidth:     1.8,
              pointRadius:     0,
              fill:            true,
              tension:         0.3,
            },
            {
              label: "Val Loss",
              data:  hist.val_loss,
              borderColor:     "#f97316",
              backgroundColor: "transparent",
              borderWidth:     1.8,
              pointRadius:     0,
              tension:         0.3,
            },
          ],
        },
        options: {
          responsive: true,
          animation:  { duration: 800 },
          plugins: {
            legend:  { labels: { color: "#e6edf3", boxWidth: 12 } },
            tooltip: { mode: "index", intersect: false },
          },
          scales: {
            x: { title: { display: true, text: "Epoch", color: "#8b949e" },
                 ticks: { maxTicksLimit: 8 } },
            y: { type: "logarithmic",
                 title: { display: true, text: "Huber Loss (log)", color: "#8b949e" } },
          },
        },
      });
    }

    // ── MAE chart ──
    const maeCtx = document.getElementById("chart-mae")?.getContext("2d");
    if (maeCtx) {
      maeChart = new Chart(maeCtx, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Train MAE (m)",
              data:  hist.mae,
              borderColor:     "#10b981",
              backgroundColor: "rgba(16,185,129,.06)",
              borderWidth:     1.8,
              pointRadius:     0,
              fill:            true,
              tension:         0.3,
            },
            {
              label: "Val MAE (m)",
              data:  hist.val_mae,
              borderColor:     "#7c3aed",
              backgroundColor: "transparent",
              borderWidth:     1.8,
              pointRadius:     0,
              tension:         0.3,
            },
          ],
        },
        options: {
          responsive: true,
          animation:  { duration: 800 },
          plugins: {
            legend:  { labels: { color: "#e6edf3", boxWidth: 12 } },
            tooltip: { mode: "index", intersect: false },
          },
          scales: {
            x: { title: { display: true, text: "Epoch", color: "#8b949e" },
                 ticks: { maxTicksLimit: 8 } },
            y: { title: { display: true, text: "MAE (m)", color: "#8b949e" } },
          },
        },
      });
    }
  } catch (e) { console.warn("chart load:", e); }
}

// ── Hero spring (static decorative) ──────────────────────────────────────────
function initSpringHero() {
  const svg = document.getElementById("hero-spring-svg");
  if (!svg) return;
  const coils = 7, amp = 14, topY = 8, len = 160, w = 60;
  const pts = [];
  const steps = coils * 32;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    pts.push(`${(w/2 + amp * Math.sin(2*Math.PI*coils*t)).toFixed(1)},${(topY + t*len).toFixed(1)}`);
  }
  svg.innerHTML = `
    <rect x="${w/2-18}" y="0" width="36" height="6" rx="2" fill="#8b949e"/>
    <polyline points="${pts.join(" ")}" fill="none" stroke="#00d4ff" stroke-width="2.2" stroke-linecap="round"/>
    <circle cx="${w/2}" cy="${topY+len+14}" r="12" fill="#f97316" opacity=".9"/>
  `;
}

// ── Particle background (canvas) ──────────────────────────────────────────────
function initParticles() {
  const canvas = document.getElementById("bg-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let W, H, particles = [];

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener("resize", resize);

  class Particle {
    constructor() { this.reset(); }
    reset() {
      this.x  = Math.random() * W;
      this.y  = Math.random() * H;
      this.vx = (Math.random() - 0.5) * 0.35;
      this.vy = (Math.random() - 0.5) * 0.35;
      this.r  = Math.random() * 1.8 + 0.4;
      this.a  = Math.random() * 0.55 + 0.15;
      this.c  = Math.random() > 0.5 ? "0,212,255" : "124,58,237";
    }
    tick() {
      this.x += this.vx; this.y += this.vy;
      if (this.x < 0 || this.x > W || this.y < 0 || this.y > H) this.reset();
    }
    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r, 0, Math.PI*2);
      ctx.fillStyle = `rgba(${this.c},${this.a})`;
      ctx.fill();
    }
  }

  for (let i = 0; i < 85; i++) particles.push(new Particle());

  function draw() {
    ctx.clearRect(0, 0, W, H);
    // Draw connections
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 110) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(0,212,255,${(1 - dist/110) * 0.12})`;
          ctx.lineWidth = 0.6;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }
    particles.forEach(p => { p.tick(); p.draw(); });
    requestAnimationFrame(draw);
  }
  draw();
}

// ── Utility ───────────────────────────────────────────────────────────────────
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
