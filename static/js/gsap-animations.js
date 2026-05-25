/**
 * CyberProp — GSAP Scroll Experience
 * Luxury real-estate animations: char reveals, parallax,
 * horizontal property strip, stat counters, section wipes.
 */

(function () {
  'use strict';

  if (typeof gsap === 'undefined') return;
  gsap.registerPlugin(ScrollTrigger);

  /* ------------------------------------------------------------------ */
  /* Helpers                                                              */
  /* ------------------------------------------------------------------ */

  /** Split an element's text into individual <span class="char"> nodes */
  function splitChars(el) {
    const original = el.innerHTML;
    const words = original.split(/(\s+)/);
    el.innerHTML = words.map(function (word) {
      if (/^\s+$/.test(word)) return word;
      const chars = word.split('').map(function (c) {
        return '<span class="char" style="display:inline-block;will-change:transform,opacity">' + c + '</span>';
      }).join('');
      return '<span class="word" style="display:inline-block;overflow:hidden">' + chars + '</span>';
    }).join('');
    return el.querySelectorAll('.char');
  }

  /** Animate a stat number from 0 to its target */
  function animateCounter(el) {
    const raw = el.getAttribute('data-target') || el.textContent;
    // Extract prefix (R), numeric value, suffix (+, %)
    const match = raw.match(/^([^0-9]*)([0-9]+(?:\.[0-9]+)?)([^0-9]*)$/);
    if (!match) {
      el.textContent = raw;
      return;
    }
    const prefix = match[1];
    const target = parseFloat(match[2]);
    const suffix = match[3];
    const isFloat = match[2].indexOf('.') !== -1;
    const decimals = isFloat ? match[2].split('.')[1].length : 0;

    const obj = { val: 0 };
    gsap.to(obj, {
      val: target,
      duration: 2,
      ease: 'power2.out',
      onUpdate: function () {
        el.textContent = prefix + obj.val.toFixed(decimals) + suffix;
      },
      onComplete: function () {
        el.textContent = raw; // ensure exact final value
      },
    });
  }

  /* ------------------------------------------------------------------ */
  /* 1. HERO — char-by-char title reveal                                 */
  /* ------------------------------------------------------------------ */

  var heroTitle = document.getElementById('heroTitle');
  var heroSubtitle = document.getElementById('heroSubtitle');
  var heroCta = document.getElementById('heroCta');
  var scrollCue = document.getElementById('scrollCue');
  var gridLines = document.getElementById('gridLines');
  var heroBorder = document.querySelector('.hero-border');

  if (heroTitle) {
    var chars = splitChars(heroTitle);
    var tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

    tl.from(chars, {
      y: '110%',
      opacity: 0,
      duration: 0.9,
      stagger: 0.028,
    });

    if (heroSubtitle) {
      tl.from(heroSubtitle, { y: 30, opacity: 0, duration: 0.8 }, '-=0.3');
    }
    if (heroCta) {
      tl.from(heroCta.children, { y: 20, opacity: 0, duration: 0.6, stagger: 0.12 }, '-=0.4');
    }
    if (scrollCue) {
      tl.to(scrollCue, { opacity: 1, duration: 0.5 }, '+=0.3');
    }
    if (heroBorder) {
      tl.to(heroBorder, { width: '100%', duration: 1.4, ease: 'power2.inOut' }, 0.4);
    }

    // Glow pulse on the .glow-text span
    var glowSpan = heroTitle.querySelector('.glow-text');
    if (glowSpan) {
      gsap.to(glowSpan, {
        textShadow: '0 0 24px rgba(0,229,255,.9), 0 0 50px rgba(0,229,255,.4)',
        duration: 2.2,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
        delay: 1.2,
      });
    }
  }

  /* ------------------------------------------------------------------ */
  /* 2. HERO — grid parallax on scroll                                   */
  /* ------------------------------------------------------------------ */

  if (gridLines) {
    gsap.to(gridLines, {
      y: 180,
      ease: 'none',
      scrollTrigger: {
        trigger: '#hero',
        start: 'top top',
        end: 'bottom top',
        scrub: 1.5,
      },
    });
  }

  /* Hero content subtle parallax */
  var heroContent = document.querySelector('.hero-content');
  if (heroContent) {
    gsap.to(heroContent, {
      y: 80,
      opacity: 0.4,
      ease: 'none',
      scrollTrigger: {
        trigger: '#hero',
        start: 'top top',
        end: '70% top',
        scrub: 1,
      },
    });
  }

  /* ------------------------------------------------------------------ */
  /* 3. MARQUEE (speed boost on scroll)                                  */
  /* ------------------------------------------------------------------ */
  var marqueeInner = document.querySelector('.marquee-inner');
  if (marqueeInner) {
    ScrollTrigger.create({
      trigger: '.marquee-band',
      start: 'top bottom',
      end: 'bottom top',
      onUpdate: function (self) {
        var speed = 28 - self.getVelocity() / 200;
        marqueeInner.style.animationDuration = Math.max(8, speed) + 's';
      },
    });
  }

  /* ------------------------------------------------------------------ */
  /* 4. STATS — counter animation on scroll into view                    */
  /* ------------------------------------------------------------------ */

  var statsSection = document.getElementById('statsSection');
  if (statsSection) {
    var statNumbers = statsSection.querySelectorAll('.stat-number');

    gsap.from(statNumbers, {
      y: 40,
      opacity: 0,
      duration: 0.7,
      stagger: 0.15,
      scrollTrigger: {
        trigger: statsSection,
        start: 'top 80%',
        once: true,
        onEnter: function () {
          statNumbers.forEach(function (el) {
            animateCounter(el);
          });
        },
      },
    });

    // Stat labels
    gsap.from(statsSection.querySelectorAll('.stat-label'), {
      opacity: 0,
      duration: 0.6,
      stagger: 0.15,
      delay: 0.3,
      scrollTrigger: {
        trigger: statsSection,
        start: 'top 80%',
        once: true,
      },
    });
  }

  /* ------------------------------------------------------------------ */
  /* 5. ABOUT — text reveal + visual parallax                            */
  /* ------------------------------------------------------------------ */

  var aboutSection = document.getElementById('aboutSection');
  if (aboutSection) {
    var aboutTextCol = aboutSection.querySelector('.about-text-col');
    var aboutVisualCol = aboutSection.querySelector('.about-visual-col');

    if (aboutTextCol) {
      var textChildren = aboutTextCol.children;
      gsap.from(textChildren, {
        x: -60,
        opacity: 0,
        duration: 0.9,
        stagger: 0.12,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: aboutSection,
          start: 'top 72%',
          once: true,
        },
      });
    }

    if (aboutVisualCol) {
      gsap.from(aboutVisualCol, {
        x: 60,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: aboutSection,
          start: 'top 72%',
          once: true,
        },
      });

      // Subtle vertical parallax on the visual column
      gsap.to(aboutVisualCol, {
        y: -30,
        ease: 'none',
        scrollTrigger: {
          trigger: aboutSection,
          start: 'top bottom',
          end: 'bottom top',
          scrub: 1.5,
        },
      });
    }
  }

  /* ------------------------------------------------------------------ */
  /* 6. SERVICES — stagger reveal                                        */
  /* ------------------------------------------------------------------ */

  var serviceCards = document.querySelectorAll('.service-card');
  if (serviceCards.length) {
    gsap.from(serviceCards, {
      y: 50,
      opacity: 0,
      duration: 0.7,
      stagger: 0.1,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: '#servicesSection',
        start: 'top 76%',
        once: true,
      },
    });
  }

  var servicesTitleEl = document.querySelector('#servicesSection .section-title');
  if (servicesTitleEl) {
    gsap.from(servicesTitleEl, {
      y: 30, opacity: 0, duration: 0.8, ease: 'power3.out',
      scrollTrigger: { trigger: '#servicesSection', start: 'top 82%', once: true },
    });
  }

  /* ------------------------------------------------------------------ */
  /* 7. FEATURED PROPERTIES — horizontal drag scroll strip               */
  /* ------------------------------------------------------------------ */

  var propsTrackWrap = document.querySelector('.props-track-wrap');
  var propsTrack = document.querySelector('.props-track');

  if (propsTrackWrap && propsTrack) {
    var propSlides = propsTrack.querySelectorAll('.prop-slide');

    // Animate slides in on section enter
    gsap.from(propSlides, {
      x: 80,
      opacity: 0,
      duration: 0.7,
      stagger: 0.1,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: '#propertiesSection',
        start: 'top 78%',
        once: true,
      },
    });

    // Drag-to-scroll
    var isDragging = false;
    var startX = 0;
    var scrollLeft = 0;

    propsTrackWrap.addEventListener('mousedown', function (e) {
      isDragging = true;
      startX = e.pageX - propsTrackWrap.offsetLeft;
      scrollLeft = propsTrackWrap.scrollLeft;
      propsTrackWrap.style.userSelect = 'none';
    });
    document.addEventListener('mouseup', function () {
      isDragging = false;
      propsTrackWrap.style.userSelect = '';
    });
    propsTrackWrap.addEventListener('mousemove', function (e) {
      if (!isDragging) return;
      e.preventDefault();
      var x = e.pageX - propsTrackWrap.offsetLeft;
      var walk = (x - startX) * 1.5;
      propsTrackWrap.scrollLeft = scrollLeft - walk;
    });

    // Touch
    var touchStartX = 0;
    var touchScrollLeft = 0;
    propsTrackWrap.addEventListener('touchstart', function (e) {
      touchStartX = e.touches[0].pageX;
      touchScrollLeft = propsTrackWrap.scrollLeft;
    }, { passive: true });
    propsTrackWrap.addEventListener('touchmove', function (e) {
      var diff = touchStartX - e.touches[0].pageX;
      propsTrackWrap.scrollLeft = touchScrollLeft + diff;
    }, { passive: true });

    // Scroll overflow so it's draggable
    propsTrackWrap.style.overflowX = 'scroll';
    propsTrackWrap.style.scrollbarWidth = 'none';
    propsTrackWrap.style.msOverflowStyle = 'none';
    var style = document.createElement('style');
    style.textContent = '.props-track-wrap::-webkit-scrollbar{display:none}';
    document.head.appendChild(style);
  }

  /* ------------------------------------------------------------------ */
  /* 8. CONTACT — slide in from sides                                    */
  /* ------------------------------------------------------------------ */

  var contactInfoCol = document.getElementById('contactInfoCol');
  var contactFormCol = document.getElementById('contactFormCol');

  if (contactInfoCol) {
    gsap.from(contactInfoCol.querySelectorAll('.contact-info-item'), {
      x: -40,
      opacity: 0,
      duration: 0.7,
      stagger: 0.12,
      ease: 'power3.out',
      scrollTrigger: { trigger: '#contact', start: 'top 74%', once: true },
    });
  }
  if (contactFormCol) {
    gsap.from(contactFormCol, {
      x: 50,
      opacity: 0,
      duration: 0.9,
      ease: 'power3.out',
      scrollTrigger: { trigger: '#contact', start: 'top 74%', once: true },
    });
  }

  /* ------------------------------------------------------------------ */
  /* 9. CTA BAND                                                         */
  /* ------------------------------------------------------------------ */

  var ctaBand = document.getElementById('ctaBand');
  if (ctaBand) {
    var ctaTitle = document.getElementById('ctaTitle');
    if (ctaTitle) {
      var ctaChars = splitChars(ctaTitle);
      gsap.from(ctaChars, {
        y: '100%',
        opacity: 0,
        duration: 0.75,
        stagger: 0.02,
        ease: 'power3.out',
        scrollTrigger: { trigger: ctaBand, start: 'top 80%', once: true },
      });
    }
    var ctaButtons = document.getElementById('ctaButtons');
    if (ctaButtons) {
      gsap.from(ctaButtons.children, {
        y: 20, opacity: 0, duration: 0.6, stagger: 0.12,
        scrollTrigger: { trigger: ctaBand, start: 'top 78%', once: true },
      });
    }
  }

  /* ------------------------------------------------------------------ */
  /* 10. PROPERTY DETAIL PAGE — GSAP reveals                            */
  /* ------------------------------------------------------------------ */

  var detailHero = document.getElementById('heroContainer');
  if (detailHero) {
    gsap.from(detailHero, { opacity: 0, scale: 1.04, duration: 1, ease: 'power3.out' });

    gsap.from('.detail-card', {
      y: 30, opacity: 0, duration: 0.7, stagger: 0.12, ease: 'power3.out',
      scrollTrigger: { trigger: '.detail-card', start: 'top 85%', once: true },
    });

    gsap.from('.stat-box', {
      y: 20, opacity: 0, duration: 0.5, stagger: 0.08, ease: 'power3.out',
      scrollTrigger: { trigger: '.stat-box', start: 'top 85%', once: true },
    });
  }

  /* ------------------------------------------------------------------ */
  /* 11. PROPERTY LIST PAGE — card stagger                               */
  /* ------------------------------------------------------------------ */

  var listCards = document.querySelectorAll('.property-card');
  if (listCards.length && !detailHero) {
    gsap.from(listCards, {
      y: 40, opacity: 0, duration: 0.65, stagger: 0.08, ease: 'power3.out',
      scrollTrigger: { trigger: listCards[0], start: 'top 90%', once: true },
    });
  }

  /* ------------------------------------------------------------------ */
  /* 12. Generic .fade-up elements (non-home pages)                      */
  /* ------------------------------------------------------------------ */

  document.querySelectorAll('.fade-up').forEach(function (el) {
    gsap.from(el, {
      y: 30, opacity: 0, duration: 0.6, ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 88%', once: true },
    });
  });

  /* ------------------------------------------------------------------ */
  /* 13. Section eyebrows & titles (generic reveal on all pages)         */
  /* ------------------------------------------------------------------ */

  document.querySelectorAll('.eyebrow, .services-eyebrow').forEach(function (el) {
    gsap.from(el, {
      x: -20, opacity: 0, duration: 0.6, ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 88%', once: true },
    });
  });

  document.querySelectorAll('.section-divider').forEach(function (el) {
    gsap.from(el, {
      width: 0, duration: 0.8, ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 90%', once: true },
    });
  });

}());

