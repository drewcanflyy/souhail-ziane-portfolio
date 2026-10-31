/* ------------------------------------------------------------------
   Souhail Ziane - motion layer
   GSAP + ScrollTrigger + SplitText. All scroll work is trigger based,
   no scroll listeners. Every animation is skipped for reduced motion.
------------------------------------------------------------------- */

(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var hasGSAP = typeof window.gsap !== 'undefined';
  var gsap = window.gsap;

  if (hasGSAP && window.ScrollTrigger) gsap.registerPlugin(window.ScrollTrigger);
  if (hasGSAP && window.SplitText) gsap.registerPlugin(window.SplitText);

  var ScrollTrigger = window.ScrollTrigger;

  function q(sel, ctx) { return (ctx || document).querySelector(sel); }
  function qa(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  /* ---------------------------------------------------------------- */
  /* Cursor + magnetics                                               */
  /* ---------------------------------------------------------------- */
  function initCursor() {
    var cursor = q('#cursor');
    if (!cursor || !finePointer || reduced || !hasGSAP) return;

    var dot = q('.cursor-dot', cursor);
    var ring = q('.cursor-ring', cursor);
    var pos = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
    var dotX = gsap.quickTo(dot, 'x', { duration: 0.08, ease: 'power2.out' });
    var dotY = gsap.quickTo(dot, 'y', { duration: 0.08, ease: 'power2.out' });
    var ringX = gsap.quickTo(ring, 'x', { duration: 0.42, ease: 'power3.out' });
    var ringY = gsap.quickTo(ring, 'y', { duration: 0.42, ease: 'power3.out' });

    var shown = false;
    window.addEventListener('pointermove', function (e) {
      if (!shown) {
        gsap.to(cursor, { opacity: 1, duration: 0.4 });
        shown = true;
      }
      dotX(e.clientX); dotY(e.clientY);
      ringX(e.clientX); ringY(e.clientY);
    }, { passive: true });

    document.addEventListener('pointerleave', function () {
      gsap.to(cursor, { opacity: 0, duration: 0.3 });
      shown = false;
    });

    document.addEventListener('pointerover', function (e) {
      var target = e.target.closest('a, button, [data-cursor]');
      cursor.classList.toggle('is-hover', !!target);
    });
    document.addEventListener('pointerdown', function () { cursor.classList.add('is-down'); });
    document.addEventListener('pointerup', function () { cursor.classList.remove('is-down'); });
  }

  function initMagnetics() {
    if (!finePointer || reduced || !hasGSAP) return;
    qa('.magnetic').forEach(function (el) {
      var strength = 0.28;
      var xTo = gsap.quickTo(el, 'x', { duration: 0.5, ease: 'power3.out' });
      var yTo = gsap.quickTo(el, 'y', { duration: 0.5, ease: 'power3.out' });

      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        xTo((e.clientX - (r.left + r.width / 2)) * strength);
        yTo((e.clientY - (r.top + r.height / 2)) * strength);
      });
      el.addEventListener('pointerleave', function () { xTo(0); yTo(0); });
    });
  }

  /* ---------------------------------------------------------------- */
  /* Accordion                                                        */
  /* ---------------------------------------------------------------- */
  function initAccordion() {
    var panels = qa('[data-panel]');
    if (!panels.length) return;

    function open(target) {
      panels.forEach(function (p) {
        var on = p === target;
        p.classList.toggle('is-open', on);
        var btn = q('.panel-toggle', p);
        if (btn) btn.setAttribute('aria-expanded', on ? 'true' : 'false');
      });
    }

    panels.forEach(function (panel) {
      var btn = q('.panel-toggle', panel);
      if (!btn) return;
      btn.addEventListener('click', function () { open(panel); });
      btn.addEventListener('focus', function () { open(panel); });
      if (finePointer) {
        panel.addEventListener('pointerenter', function () { open(panel); });
      }
    });

    open(panels[0]);
  }

  /* ---------------------------------------------------------------- */
  /* Nav state, progress, marquee                                     */
  /* ---------------------------------------------------------------- */
  function initChrome() {
    var nav = q('#nav');
    var bar = q('#scrollProgress span');

    if (hasGSAP && ScrollTrigger) {
      ScrollTrigger.create({
        start: 48,
        end: 'max',
        onToggle: function (self) { if (nav) nav.classList.toggle('is-stuck', self.isActive); }
      });

      if (bar) {
        ScrollTrigger.create({
          start: 0,
          end: 'max',
          onUpdate: function (self) { gsap.set(bar, { scaleX: self.progress }); }
        });
      }

      qa('.nav-links a').forEach(function (link) {
        var id = link.getAttribute('data-nav');
        var section = id ? document.getElementById(id) : null;
        if (!section) return;
        ScrollTrigger.create({
          trigger: section,
          start: 'top 45%',
          end: 'bottom 45%',
          onToggle: function (self) { link.classList.toggle('is-active', self.isActive); }
        });
      });
    }
  }

  function initMarquee() {
    var track = q('#marqueeTrack');
    if (!track || reduced || !hasGSAP) return;

    var tween = gsap.to(track, {
      xPercent: -50,
      repeat: -1,
      duration: 30,
      ease: 'none'
    });

    if (ScrollTrigger) {
      var boost = 1;
      ScrollTrigger.create({
        start: 0,
        end: 'max',
        onUpdate: function (self) {
          var v = Math.min(Math.abs(self.getVelocity()) / 1400, 2.5);
          var target = 1 + v;
          if (Math.abs(target - boost) < 0.06) return;
          boost = target;
          gsap.to(tween, { timeScale: boost, duration: 0.6, overwrite: true });
        }
      });
    }
  }

  /* ---------------------------------------------------------------- */
  /* Mobile menu                                                      */
  /* ---------------------------------------------------------------- */
  function initMenu() {
    var btn = q('#menuToggle');
    var menu = q('#siteMenu');
    if (!btn || !menu) return;

    var label = q('.menu-label', btn);
    var links = qa('.site-menu-nav a', menu);
    var isOpen = false;
    var busy = false;

    function openMenu() {
      if (isOpen || busy) return;
      isOpen = true;
      busy = true;
      menu.hidden = false;
      btn.setAttribute('aria-expanded', 'true');
      if (label) label.textContent = 'Close';
      document.body.classList.add('menu-open');

      if (hasGSAP && !reduced) {
        gsap.set(menu, { clipPath: 'inset(0 0 100% 0)' });
        gsap.timeline({ onComplete: function () { busy = false; } })
          .to(menu, { clipPath: 'inset(0 0 0% 0)', duration: 0.65, ease: 'power4.inOut' })
          .from(links, { yPercent: 30, opacity: 0, duration: 0.55, stagger: 0.05, ease: 'power3.out' }, '-=0.35');
      } else {
        busy = false;
      }

      if (links[0]) setTimeout(function () { links[0].focus({ preventScroll: true }); }, 120);
    }

    function closeMenu() {
      if (!isOpen || busy) return;
      isOpen = false;
      busy = true;
      btn.setAttribute('aria-expanded', 'false');
      if (label) label.textContent = 'Menu';
      document.body.classList.remove('menu-open');

      var done = function () {
        menu.hidden = true;
        busy = false;
      };

      if (hasGSAP && !reduced) {
        gsap.to(menu, { clipPath: 'inset(0 0 100% 0)', duration: 0.5, ease: 'power4.inOut', onComplete: done });
      } else {
        done();
      }
    }

    btn.addEventListener('click', function () { isOpen ? closeMenu() : openMenu(); });
    links.forEach(function (a) { a.addEventListener('click', closeMenu); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen) closeMenu();
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 900 && isOpen) closeMenu();
    });
  }

  /* ---------------------------------------------------------------- */
  /* Scroll choreography                                             */
  /* ---------------------------------------------------------------- */
  function revealTitle(el, delay) {
    if (!hasGSAP) return;
    if (window.SplitText) {
      var split = new window.SplitText(el, { type: 'lines', linesClass: 'split-line' });
      split.lines.forEach(function (line) {
        line.style.overflow = 'hidden';
        var inner = document.createElement('span');
        inner.style.display = 'block';
        inner.innerHTML = line.innerHTML;
        line.innerHTML = '';
        line.appendChild(inner);
        gsap.from(inner, {
          yPercent: 105,
          duration: 1.15,
          delay: delay || 0,
          ease: 'power4.out',
          scrollTrigger: { trigger: el, start: 'top 85%', once: true }
        });
      });
    } else {
      gsap.from(el, { y: 40, opacity: 0, duration: 1, ease: 'power3.out' });
    }
  }

  function initScrollScenes() {
    if (!hasGSAP || !ScrollTrigger || reduced) return;

    /* hero parallax */
    var heroImg = q('.hero-media img');
    if (heroImg) {
      gsap.to(heroImg, {
        yPercent: 8,
        ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true }
      });
    }

    /* section titles with masked lines */
    qa('.section-title').forEach(function (el) { revealTitle(el); });

    /* statement word scrub */
    var statement = q('#statementText');
    if (statement && window.SplitText) {
      var words = new window.SplitText(statement, { type: 'words', wordsClass: 'word' }).words;
      gsap.to(words, {
        color: '#f2eee5',
        stagger: 0.08,
        ease: 'none',
        scrollTrigger: {
          trigger: statement,
          start: 'top 78%',
          end: 'bottom 52%',
          scrub: 0.6
        }
      });
    }

    /* featured media clip reveal */
    qa('.reveal-media').forEach(function (el) {
      gsap.fromTo(el, { clipPath: 'inset(0% 0% 100% 0%)' }, {
        clipPath: 'inset(0% 0% 0% 0%)',
        duration: 1.3,
        ease: 'power3.inOut',
        scrollTrigger: { trigger: el, start: 'top 82%', once: true }
      });
    });

    /* project stack scaling */
    var cards = qa('.project');
    cards.forEach(function (card, i) {
      if (i < cards.length - 1) {
        gsap.to(card, {
          scale: 0.94,
          ease: 'none',
          scrollTrigger: {
            trigger: cards[i + 1],
            start: 'top 92%',
            end: 'top 30%',
            scrub: true
          }
        });
      }
    });

    /* steps: highlight current */
    qa('.step').forEach(function (step) {
      ScrollTrigger.create({
        trigger: step,
        start: 'top 62%',
        end: 'bottom 62%',
        onToggle: function (self) { step.classList.toggle('is-current', self.isActive); }
      });
    });

    /* bento cells rise */
    qa('.cell').forEach(function (cell, i) {
      gsap.from(cell, {
        y: 34,
        opacity: 0,
        duration: 1,
        delay: i * 0.06,
        ease: 'power3.out',
        scrollTrigger: { trigger: '.bento', start: 'top 78%', once: true }
      });
    });

    /* contact title */
    var contactTitle = q('.contact-title');
    if (contactTitle && window.SplitText) {
      var csplit = new window.SplitText(contactTitle, { type: 'lines' });
      csplit.lines.forEach(function (line) {
        line.style.overflow = 'hidden';
        var inner = document.createElement('span');
        inner.style.display = 'block';
        inner.innerHTML = line.innerHTML;
        line.innerHTML = '';
        line.appendChild(inner);
        gsap.from(inner, {
          yPercent: 105,
          duration: 1.2,
          stagger: 0.08,
          ease: 'power4.out',
          scrollTrigger: { trigger: contactTitle, start: 'top 84%', once: true }
        });
      });
    }
  }

  /* ---------------------------------------------------------------- */
  /* Intro                                                            */
  /* ---------------------------------------------------------------- */
  function initIntro() {
    var loader = q('#loader');
    var count = q('#loaderCount');
    var bar = q('#loaderBar');
    var heroTitle = q('#heroTitle');
    var heroSub = q('.hero-sub');
    var heroEyebrow = q('.hero-eyebrow');
    var heroActions = q('.hero-actions');
    var heroVisual = q('#heroVisual');

    if (reduced || !hasGSAP || !loader) {
      if (loader) loader.style.display = 'none';
      document.body.classList.remove('is-loading');
      return;
    }

    document.body.classList.remove('is-loading');
    document.body.classList.add('is-loading');

    var counter = { value: 0 };
    var tl = gsap.timeline();

    tl.to(counter, {
      value: 100,
      duration: 0.65,
      ease: 'power2.inOut',
      onUpdate: function () {
        if (count) count.textContent = String(Math.round(counter.value)).padStart(2, '0');
      }
    }, 0)
      .to(bar, { scaleX: 1, duration: 0.65, ease: 'power2.inOut' }, 0)
      .to('.loader-top, .loader-bottom, .loader-bar', { opacity: 0, duration: 0.25, ease: 'power2.out' }, 0.68)
      .to(loader, {
        yPercent: -100,
        duration: 0.72,
        ease: 'power4.inOut',
        onComplete: function () {
          loader.style.display = 'none';
          document.body.classList.remove('is-loading');
          ScrollTrigger && ScrollTrigger.refresh();
        }
      }, 0.78);

    /* hero reveal */
    var lines = qa('#heroTitle .title-line > span');
    gsap.set([heroEyebrow, heroSub, heroActions], { opacity: 0, y: 18 });
    gsap.set(lines, { yPercent: 110 });
    gsap.set(heroVisual, { opacity: 0 });
    gsap.set(q('.hero-media', heroVisual), { clipPath: 'inset(0% 0% 100% 0%)' });
    gsap.set(q('.hero-media img', heroVisual), { scale: 1.28 });

    var intro = gsap.timeline({ delay: 1.05 });
    intro
      .to(heroEyebrow, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' })
      .to(lines, { yPercent: 0, duration: 1.15, ease: 'power4.out', stagger: 0.09 }, 0.08)
      .to(heroVisual, { opacity: 1, duration: 1.1, ease: 'power2.out' }, 0.15)
      .to(q('.hero-media', heroVisual), { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.2, ease: 'power4.inOut' }, 0.15)
      .to(q('.hero-media img', heroVisual), { scale: 1.12, duration: 1.4, ease: 'power3.out' }, 0.15)
      .to(heroSub, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out' }, 0.55)
      .to(heroActions, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out' }, 0.68)
      .add(function () { ScrollTrigger && ScrollTrigger.refresh(); });
  }

  /* ---------------------------------------------------------------- */
  /* Boot                                                             */
  /* ---------------------------------------------------------------- */
  function boot() {
    initCursor();
    initMagnetics();
    initAccordion();
    initMenu();
    initChrome();
    initMarquee();

    var started = false;

    function start() {
      if (started) return;
      started = true;
      if (!reduced && hasGSAP) {
        initScrollScenes();
        initIntro();
        if (ScrollTrigger) setTimeout(function () { ScrollTrigger.refresh(); }, 120);
      } else {
        var loader = q('#loader');
        if (loader) loader.style.display = 'none';
        document.body.classList.remove('is-loading');
      }
    }

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(start);
      setTimeout(start, 900);
    } else {
      start();
    }

    if (hasGSAP && ScrollTrigger) {
      window.addEventListener('load', function () { ScrollTrigger.refresh(); });
      var resizeTimer;
      window.addEventListener('resize', function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () { ScrollTrigger.refresh(); }, 300);
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
