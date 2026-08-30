// Automatic language detection (EN/ES).
//
// The HTML ships with English as the default markup. Elements that should be
// translatable carry a data-i18n="key" attribute; this module swaps their text
// at runtime. The active language is chosen from localStorage when a preference
// was previously saved, otherwise detected from the browser/system language
// (navigator.language). This is a browser-language preference, not a page
// translate button: there is no visible language UI.
(function () {
  'use strict';

  var STORAGE_KEY = 'lang';

  var dict = {
    en: {
      'nav.skills': 'skills',
      'nav.experience': 'experience',
      'nav.contact': 'contact',
      'nav.cv': 'cv.pdf',
      'skill.docker': 'Containers, images, compose, orchestration',
      'skill.linux': 'Administration, networking, shell scripting',
      'skill.cicd': 'GitHub Actions, automated pipelines',
      'skill.git': 'Version control, branching, PRs, collaboration',
      'skill.python': 'Automation, scripting, APIs, AI/ML',
      'skill.bash': 'Shell scripting, automation, system tools',
      'skill.ansible': 'Configuration management, playbooks',
      'skill.vagrant': 'VM provisioning, dev environments',
      'skill.github': 'Version control, branching, PRs, collaboration, GitHub Projects, GitHub Secrets',
      'exp.geekclub.role': 'Community Leader — GeekClub',
      'exp.geekclub.desc': 'Lead a 90+ member tech community focused on open source. Organize weekly events, workshops, and in-person talks at public schools. Manage activities via GitHub, Notion, and Discord.',
      'exp.ohmybash.role': 'Open Source Contributor — Oh My Bash',
      'exp.ohmybash.desc': 'Contributed to official documentation: documented prompt styles and Git-related plugin functions.',
      'exp.samsung.role': 'Developer · DevOps — Samsung Innovation Campus',
      'exp.samsung.desc': 'Collaborated with people from around the world on AI and Python projects. Handled documentation, version control systems, and CI integration.',
      'exp.freelance.role': 'Service Assistant — Freelance',
      'exp.freelance.desc': 'Created automated quotes and technical reports with Python, Excel, and Word. Served multilingual clients (Spanish, English).',
      'posts.label': 'in the field',
      'posts.me-teaching': 'Teaching the campus',
      'posts.news-room': 'News room, Latinoamérica',
      'posts.semana-global': 'Global Entrepreneurship Week team',
      'posts.sic-team': 'Samsung Innovation Campus team',
      'posts.sic-working': 'Working with the SIC team'
    },
    es: {
      'nav.skills': 'habilidades',
      'nav.experience': 'experiencia',
      'nav.contact': 'contacto',
      'nav.cv': 'cv.pdf',
      'skill.docker': 'Contenedores, imágenes, compose, orquestación',
      'skill.linux': 'Administración, redes, scripting de shell',
      'skill.cicd': 'GitHub Actions, pipelines automatizados',
      'skill.git': 'Control de versiones, ramas, PRs, colaboración',
      'skill.python': 'Automatización, scripting, APIs, IA/ML',
      'skill.bash': 'Scripting de shell, automatización, herramientas del sistema',
      'skill.ansible': 'Gestión de configuración, playbooks',
      'skill.vagrant': 'Aprovisionamiento de VMs, entornos de desarrollo',
      'skill.github': 'Control de versiones, ramas, PRs, colaboración, GitHub Projects, GitHub Secrets',
      'exp.geekclub.role': 'Líder de Comunidad — GeekClub',
      'exp.geekclub.desc': 'Lidero una comunidad tech de más de 90 miembros enfocada en open source. Organizo eventos semanales, talleres y charlas presenciales en escuelas públicas. Gestiono actividades vía GitHub, Notion y Discord.',
      'exp.ohmybash.role': 'Contribuidor Open Source — Oh My Bash',
      'exp.ohmybash.desc': 'Contribuí a la documentación oficial: documenté estilos de prompt y funciones de plugins relacionados con Git.',
      'exp.samsung.role': 'Desarrollador · DevOps — Samsung Innovation Campus',
      'exp.samsung.desc': 'Colaboré con personas de todo el mundo en proyectos de IA y Python. Manejé documentación, sistemas de control de versiones e integración de CI.',
      'exp.freelance.role': 'Asistente de Servicio — Freelance',
      'exp.freelance.desc': 'Creé cotizaciones automatizadas e informes técnicos con Python, Excel y Word. Atendí clientes multilingües (español, inglés).',
      'posts.label': 'en el campo',
      'posts.me-teaching': 'Enseñando en el campus',
      'posts.news-room': 'Sala de prensa, Latinoamérica',
      'posts.semana-global': 'Equipo de la Semana Global del Emprendimiento',
      'posts.sic-team': 'Equipo del Samsung Innovation Campus',
      'posts.sic-working': 'Trabajando con el equipo del SIC'
    }
  };

  function detectLang() {
    var saved = null;
    try {
      saved = window.localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      saved = null;
    }
    if (saved === 'es' || saved === 'en') {
      return saved;
    }
    var nav = (window.navigator.language || 'en').toLowerCase();
    return nav.indexOf('es') === 0 ? 'es' : 'en';
  }

  function apply(lang) {
    var strings = dict[lang];
    var nodes = document.querySelectorAll('[data-i18n]');
    Array.prototype.forEach.call(nodes, function (node) {
      var key = node.getAttribute('data-i18n');
      if (key in strings) {
        node.textContent = strings[key];
      } else if (lang === 'es') {
        // No Spanish value: keep the English default already in the markup.
        node.textContent = dict.en[key];
      }
    });
    document.documentElement.setAttribute('lang', lang);
    try {
      window.localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {
      /* persistence is best-effort; ignore quota/private-mode errors */
    }
  }

  function init() {
    apply(detectLang());
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
