/**
 * CyberProp GSAP Animations
 * Uses GSAP ScrollTrigger for scroll-based animations on the homepage hero
 * and section reveals throughout the site.
 */

document.addEventListener('DOMContentLoaded', function () {
  // Register GSAP plugins
  if (typeof gsap === 'undefined') return;

  gsap.registerPlugin(ScrollTrigger);

  // --- Hero Section Animations ---
  const heroTitle = document.querySelector('.hero-title');
  const heroSubtitle = document.querySelector('.hero-subtitle');
  const heroCta = document.querySelector('.hero-cta');
  const gridLines = document.querySelector('.grid-lines');

  if (heroTitle) {
    const heroTl = gsap.timeline({ defaults: { ease: 'power3.out' } });

    heroTl
      .from(heroTitle, {
        y: 60,
        opacity: 0,
        duration: 1,
      })
      .from(
        heroSubtitle,
        {
          y: 40,
          opacity: 0,
          duration: 0.8,
        },
        '-=0.4'
      )
      .from(
        heroCta,
        {
          y: 30,
          opacity: 0,
          duration: 0.6,
        },
        '-=0.3'
      );
  }

  // Parallax effect on grid lines
  if (gridLines) {
    gsap.to(gridLines, {
      y: 150,
      ease: 'none',
      scrollTrigger: {
        trigger: '.hero-section',
        start: 'top top',
        end: 'bottom top',
        scrub: true,
      },
    });
  }

  // --- Stat Cards Stagger Animation ---
  const statCards = document.querySelectorAll('.stat-card');
  if (statCards.length) {
    gsap.from(statCards, {
      y: 50,
      opacity: 0,
      duration: 0.6,
      stagger: 0.15,
      scrollTrigger: {
        trigger: statCards[0].closest('.section-padding') || statCards[0],
        start: 'top 80%',
        toggleActions: 'play none none none',
      },
    });
  }

  // --- Feature Cards Stagger Animation ---
  const featureCards = document.querySelectorAll('.feature-card');
  if (featureCards.length) {
    gsap.from(featureCards, {
      y: 40,
      opacity: 0,
      duration: 0.6,
      stagger: 0.12,
      scrollTrigger: {
        trigger: featureCards[0].closest('.section-padding') || featureCards[0],
        start: 'top 80%',
        toggleActions: 'play none none none',
      },
    });
  }

  // --- Property Cards Stagger Animation ---
  const propertyCards = document.querySelectorAll('.property-card');
  if (propertyCards.length) {
    gsap.from(propertyCards, {
      y: 40,
      opacity: 0,
      duration: 0.5,
      stagger: 0.1,
      scrollTrigger: {
        trigger: propertyCards[0].closest('.section-padding') || propertyCards[0],
        start: 'top 80%',
        toggleActions: 'play none none none',
      },
    });
  }

  // --- CTA Section Reveal ---
  const ctaSection = document.querySelector('.cta-section');
  if (ctaSection) {
    gsap.from(ctaSection.children, {
      y: 30,
      opacity: 0,
      duration: 0.8,
      stagger: 0.15,
      scrollTrigger: {
        trigger: ctaSection,
        start: 'top 85%',
        toggleActions: 'play none none none',
      },
    });
  }

  // --- Generic fade-up elements ---
  const fadeUpElements = document.querySelectorAll('.fade-up');
  fadeUpElements.forEach(function (el) {
    gsap.from(el, {
      y: 30,
      opacity: 0,
      duration: 0.6,
      scrollTrigger: {
        trigger: el,
        start: 'top 85%',
        toggleActions: 'play none none none',
      },
    });
  });

  // --- Hero text glow pulse ---
  const glowTexts = document.querySelectorAll('.glow-text');
  glowTexts.forEach(function (el) {
    gsap.to(el, {
      textShadow: '0 0 20px rgba(0,229,255,0.8), 0 0 40px rgba(0,229,255,0.4)',
      duration: 2,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
    });
  });
});
