/**
 * PNU Physics - Main JavaScript
 * Navbar, Scroll Animations, Tabs, Counter
 */

document.addEventListener('DOMContentLoaded', function () {
  // ── Navbar scroll effect ──────────────────
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      navbar.classList.add('navbar-scrolled');
    } else {
      navbar.classList.remove('navbar-scrolled');
    }
  });

  // ── Mobile menu toggle ────────────────────
  const menuBtn = document.getElementById('menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  const menuIcon = document.getElementById('menu-icon');
  const closeIcon = document.getElementById('close-icon');

  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', () => {
      const isOpen = !mobileMenu.classList.contains('hidden');
      if (isOpen) {
        mobileMenu.classList.add('hidden');
        menuIcon.classList.remove('hidden');
        closeIcon.classList.add('hidden');
      } else {
        mobileMenu.classList.remove('hidden');
        menuIcon.classList.add('hidden');
        closeIcon.classList.remove('hidden');
      }
    });

    // Close on link click
    mobileMenu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        mobileMenu.classList.add('hidden');
        menuIcon.classList.remove('hidden');
        closeIcon.classList.add('hidden');
      });
    });
  }

  // ── Scroll-triggered animations ───────────
  const animElements = document.querySelectorAll('.fade-up, .fade-left, .fade-right');
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
  );
  animElements.forEach((el) => observer.observe(el));

  // ── Counter animation ─────────────────────
  function animateCounter(el, target, duration = 2000, suffix = '') {
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= target) {
        start = target;
        clearInterval(timer);
      }
      el.textContent = Math.floor(start).toLocaleString() + suffix;
    }, 16);
  }

  const counterObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && !entry.target.dataset.counted) {
          entry.target.dataset.counted = 'true';
          const target = parseInt(entry.target.dataset.target, 10);
          const suffix = entry.target.dataset.suffix || '';
          animateCounter(entry.target, target, 2000, suffix);
        }
      });
    },
    { threshold: 0.5 }
  );

  document.querySelectorAll('.count-up').forEach((el) => counterObserver.observe(el));

  // ── Research tabs ─────────────────────────
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  tabBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;

      tabBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');

      tabPanels.forEach((panel) => {
        if (panel.dataset.panel === target) {
          panel.classList.remove('hidden');
          panel.style.opacity = '0';
          setTimeout(() => {
            panel.style.transition = 'opacity 0.4s ease';
            panel.style.opacity = '1';
          }, 10);
        } else {
          panel.classList.add('hidden');
        }
      });
    });
  });

  // ── Active nav link on scroll ─────────────
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');

  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach((sec) => {
      if (window.scrollY >= sec.offsetTop - 100) {
        current = sec.id;
      }
    });
    navLinks.forEach((link) => {
      link.classList.remove('text-blue-400');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('text-blue-400');
      }
    });
  });

  // ── Smooth scroll for anchor links ────────
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', (e) => {
      const href = anchor.getAttribute('href');
      if (href === '#') return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        const offset = 80;
        window.scrollTo({
          top: target.offsetTop - offset,
          behavior: 'smooth',
        });
      }
    });
  });

  // ── Faculty filter ─────────────────────────
  const filterBtns = document.querySelectorAll('.filter-btn');
  const facultyCards = document.querySelectorAll('.faculty-card-wrapper');

  filterBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      filterBtns.forEach((b) => {
        b.classList.remove('bg-blue-600', 'text-white');
        b.classList.add('text-slate-400');
      });
      btn.classList.add('bg-blue-600', 'text-white');
      btn.classList.remove('text-slate-400');

      const filter = btn.dataset.filter;
      facultyCards.forEach((card) => {
        if (filter === 'all' || card.dataset.specialty === filter) {
          card.style.display = '';
          card.classList.add('fade-up', 'visible');
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // ── Hero CTA button ripple ─────────────────
  document.querySelectorAll('.btn-ripple').forEach((btn) => {
    btn.addEventListener('click', function (e) {
      const ripple = document.createElement('span');
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      ripple.style.cssText = `
        position:absolute; border-radius:50%; pointer-events:none;
        width:${size}px; height:${size}px;
        left:${e.clientX - rect.left - size / 2}px;
        top:${e.clientY - rect.top - size / 2}px;
        background:rgba(255,255,255,0.3);
        transform:scale(0); animation:ripple 0.6s linear;
      `;
      this.style.position = 'relative';
      this.style.overflow = 'hidden';
      this.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  });

  // Add ripple keyframe
  const style = document.createElement('style');
  style.textContent = `@keyframes ripple { to { transform: scale(4); opacity: 0; } }`;
  document.head.appendChild(style);

  // ── Typed text effect (hero) ───────────────
  const typedEl = document.getElementById('typed-text');
  if (typedEl) {
    const phrases = ['물리의 세계로', '미래를 탐구하다', '우주를 이해하다', '양자를 제어하다'];
    let phraseIdx = 0;
    let charIdx = 0;
    let isDeleting = false;
    let typingSpeed = 120;

    function type() {
      const current = phrases[phraseIdx];
      if (isDeleting) {
        typedEl.textContent = current.substring(0, charIdx - 1);
        charIdx--;
        typingSpeed = 60;
      } else {
        typedEl.textContent = current.substring(0, charIdx + 1);
        charIdx++;
        typingSpeed = 120;
      }

      if (!isDeleting && charIdx === current.length) {
        isDeleting = true;
        typingSpeed = 1500;
      } else if (isDeleting && charIdx === 0) {
        isDeleting = false;
        phraseIdx = (phraseIdx + 1) % phrases.length;
        typingSpeed = 400;
      }

      setTimeout(type, typingSpeed);
    }

    setTimeout(type, 1000);
  }
});
