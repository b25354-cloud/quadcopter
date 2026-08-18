(function () {
  'use strict';

  var navToggle = document.getElementById('nav-toggle');
  var navLinks = document.getElementById('nav-links');

  function closeNav() {
    navLinks.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  }

  if (navToggle) {
    navToggle.addEventListener('click', function () {
      var open = navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', String(open));
    });
  }

  document.querySelectorAll('.nav-links a').forEach(function (link) {
    link.addEventListener('click', closeNav);
  });

  document.addEventListener('click', function (event) {
    if (!navLinks) return;
    var inHeader = navLinks.contains(event.target) || navToggle.contains(event.target);
    if (!inHeader && navLinks.classList.contains('open')) {
      closeNav();
    }
  });

  var header = document.getElementById('site-header');
  var backToTop = document.getElementById('back-to-top');
  if (header && backToTop) {
    var scrolled = function () {
      header.classList.toggle('scrolled', window.scrollY > 8);
      backToTop.classList.toggle('show', window.scrollY > 480);
    };
    window.addEventListener('scroll', scrolled, { passive: true });
    scrolled();
  }

  var year = document.getElementById('year');
  if (year) {
    year.textContent = String(new Date().getFullYear());
  }

  var revealSelectors = '.section-head, .about-card, .feature-item, .arch-card, .spec-table, .chip, .step, .sponsor-card';
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function staggerWithin(elements) {
    var seen = 0;
    var bucket = {};
    elements.forEach(function (el) {
      var parent = el.parentNode;
      if (!bucket[parent]) {
        bucket[parent] = seen++;
      }
      var delay = Math.min(bucket[parent] * 90, 540);
      el.style.transitionDelay = delay + 'ms';
    });
  }

  var revealEls = Array.prototype.slice.call(document.querySelectorAll(revealSelectors));
  if (reduceMotion) {
    revealEls.forEach(function (el) { el.classList.add('in-view'); });
  } else {
    staggerWithin(revealEls);
    revealEls.forEach(function (el) { el.classList.add('reveal'); });
    if ('IntersectionObserver' in window) {
      var revealObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('in-view');
            revealObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
      revealEls.forEach(function (el) { revealObserver.observe(el); });
    } else {
      revealEls.forEach(function (el) { el.classList.add('in-view'); });
    }
  }

  var navAnchors = Array.prototype.slice.call(document.querySelectorAll('.nav-links a[href^="#"]'));
  var sections = navAnchors
    .map(function (a) { return document.querySelector(a.getAttribute('href')); })
    .filter(Boolean);

  function setActive(id) {
    navAnchors.forEach(function (a) {
      var active = a.getAttribute('href') === '#' + id;
      a.classList.toggle('active', active);
    });
  }

  if ('IntersectionObserver' in window && sections.length) {
    var sectionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          setActive(entry.target.id);
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach(function (s) { sectionObserver.observe(s); });
  }

  var typed = document.querySelector('.typewriter');
  if (typed && !reduceMotion) {
    var text = typed.textContent;
    var speed = 18;
    var i = 0;
    typed.classList.add('typing');
    typed.textContent = '';
    function typeNext() {
      if (i < text.length) {
        typed.textContent = text.slice(0, ++i);
        setTimeout(typeNext, speed);
      } else {
        typed.classList.remove('typing');
      }
    }
    setTimeout(typeNext, 400);
  }
})();