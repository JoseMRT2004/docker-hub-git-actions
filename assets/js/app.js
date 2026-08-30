// Typing animation
(function () {
  const el = document.getElementById('typing');
  const phrases = [
    'Automating infrastructure...',
    'Building solutions...',
    'Breaking barriers...'
  ];
  let phraseIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  let isPaused = false;

  function type() {
    const current = phrases[phraseIndex];

    if (isPaused) {
      setTimeout(type, 1500);
      isPaused = false;
      isDeleting = true;
      return;
    }

    if (isDeleting) {
      el.textContent = current.substring(0, charIndex - 1);
      charIndex--;

      if (charIndex === 0) {
        isDeleting = false;
        phraseIndex = (phraseIndex + 1) % phrases.length;
        setTimeout(type, 400);
        return;
      }
      setTimeout(type, 25);
    } else {
      el.textContent = current.substring(0, charIndex + 1);
      charIndex++;

      if (charIndex === current.length) {
        isPaused = true;
        setTimeout(type, 0);
        return;
      }
      setTimeout(type, 50);
    }
  }

  type();
})();

// Scroll reveal
(function () {
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) {
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, {threshold: 0.1});

  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
})();

// Certificate lightbox — click a cert thumbnail to see it at full size.
(function () {
  const lightbox = document.getElementById('cert-lightbox');
  const img = document.getElementById('cert-lightbox-img');
  const caption = document.getElementById('cert-lightbox-caption');
  const close = document.getElementById('cert-lightbox-close');
  if (!lightbox || !img || !caption || !close) return;

  function openLightbox(btn) {
    img.src = btn.dataset.certImg;
    img.alt = btn.title;
    const name = btn.querySelector('.cert-name');
    caption.textContent = name ? name.textContent : btn.title;
    lightbox.hidden = false;
    document.body.classList.add('lightbox-open');
    close.focus();
  }

  function closeLightbox() {
    lightbox.hidden = true;
    img.removeAttribute('src');
    document.body.classList.remove('lightbox-open');
  }

  document.querySelectorAll('.cert-item').forEach(function (btn) {
    btn.addEventListener('click', function () { openLightbox(btn); });
  });
  close.addEventListener('click', closeLightbox);
  lightbox.addEventListener('click', function (e) {
    if (e.target === lightbox) closeLightbox();
  });
  document.addEventListener('keydown', function (e) {
    if (!lightbox.hidden && e.key === 'Escape') closeLightbox();
  });
})();

/* Snake pointer is a scroll-depth hint: fade it out while the user scrolls
   and bring it back when they return to the top. */
(function () {
  var pointer = document.querySelector('.cert-pointer');
  if (!pointer) return;
  var toggle = function () {
    pointer.classList.toggle('cert-pointer--hidden', window.scrollY > 12);
  };
  toggle();
  window.addEventListener('scroll', toggle, { passive: true });
})();

