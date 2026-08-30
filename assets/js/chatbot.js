// Terminal-style FAQ chat widget — pure frontend, rules-based.
//
// No backend, no network calls, no external API. This widget answers
// predefined questions about Jose M. Taveras (who he is, DevOps stack,
// experience, contact/hiring, CV) by matching keywords in the user's
// message against a static FAQ table. If nothing matches, it falls back
// to a mailto button pre-filled with the user's text.
//
// Widget copy is English-only and deliberately NOT wired into the i18n
// module (a browser-language preference for the page body); the chat stays
// in English no matter the detected language.
(function () {
  'use strict';

  var EMAIL = 'mrtaveras.19@gmail.com';
  var MAIL_SUBJECT = 'Portfolio inquiry — Jose M. Taveras';
  var MAIL_DEFAULT_BODY = "Hi Jose, I found your portfolio and I'd like to get in touch.";

  var GREETING =
    "Hi! I'm a terminal-style FAQ bot for Jose M. Taveras's portfolio. " +
    'Ask me about who he is, his DevOps stack, experience, or how to ' +
    'contact/hire him — or tap a quick question below.';

  var FALLBACK =
    "I'm a small rules-based bot, so I didn't catch that. I can answer " +
    'about: who Jose is, his DevOps stack, experience (GeekClub, Oh My ' +
    'Bash, Samsung, freelance), contact & hiring, and the CV (cv.pdf). ' +
    'For anything else, hit the button below — it opens a mail draft with ' +
    'your message pre-filled.';

  // Ordered most-specific first: the first rule whose ANY keyword is a
  // substring of the lowercased user message wins.
  var FAQ = [
    {
      keywords: ['geekclub', 'community leader', 'community', 'leader', 'comunidad'],
      answer: 'Jose leads GeekClub, a 90+ member tech community focused on open source. He organizes weekly events, workshops, and in-person talks at public schools, managing activities through GitHub, Notion, and Discord.'
    },
    {
      keywords: ['oh my bash', 'ohmybash', 'open source'],
      answer: 'Jose is an Open Source Contributor for Oh My Bash (Feb 2024): he contributed to the official documentation, documenting prompt styles and Git-related plugin functions.'
    },
    {
      keywords: ['samsung', 'innovation campus', 'machine learning'],
      answer: 'As Developer · DevOps at Samsung Innovation Campus (2025, remote), Jose collaborated with people from around the world on AI and Python projects, handling documentation, version control systems, and CI integration.'
    },
    {
      keywords: ['cv', 'resume', 'curriculum', 'hoja de vida', 'pdf'],
      answer: 'Grab his CV with the cv.pdf button in the top bar, the hero section, or the footer of this page — it downloads JoseMTaveras_CV.pdf.'
    },
    {
      keywords: ['contact', 'hire', 'email', 'reach', 'work with', 'job', 'employ', 'contacto', 'contratar', 'correo'],
      answer: 'To contact or hire Jose, email mrtaveras.19@gmail.com (button below), or reach him on GitHub @JoseMRT2004, LinkedIn (jose-m-taveras-reyes), and TikTok @_name_.dev.',
      offerEmail: true
    },
    {
      keywords: ['docker', 'linux', 'ci/cd', 'cicd', 'github actions', 'ansible', 'vagrant', 'bash', 'python', 'devops', 'infrastructure', 'automation', 'pipeline', 'stack', 'tools', 'technolog', 'tecnologias'],
      answer: 'His DevOps stack: Docker for containers, Linux for administration, GitHub Actions for CI/CD, Ansible for configuration management, Vagrant for dev environments, and Python + Bash for automation — all glued together with Git/GitHub.'
    },
    {
      keywords: ['skill', 'know', 'sabes', 'saber', 'habilidades'],
      answer: 'Core skills: Docker, Linux, CI/CD (GitHub Actions), Git/GitHub, Python, Bash, Ansible, and Vagrant. His specialty is automating infrastructure so deployments ship themselves.'
    },
    {
      keywords: ['experience', 'background', 'career', 'history', 'freelance', 'experiencia', 'trayectoria'],
      answer: 'Experience highlights: Community Leader — GeekClub (90+ member tech community, weekly events and workshops), Open Source Contributor — Oh My Bash (official documentation), Developer · DevOps — Samsung Innovation Campus (AI/Python, version control, CI integration), and Freelance Service Assistant (automated quotes and technical reports with Python, Excel, and Word).'
    },
    {
      keywords: ['whoami', 'who are you', 'who is jose', 'about jose', 'introduce yourself', 'yourself', 'biography', 'sobre jose', 'quien es'],
      answer: 'Jose M. Taveras is a Software Developer and DevOps from the Dominican Republic, studying at ITLA — "Automating infrastructure, building solutions, breaking barriers." He is also the Community Leader of GeekClub.'
    }
  ];

  // Clickable quick-start questions rendered as chips under the log.
  var QUICK_QUESTIONS = [
    'Who is Jose M. Taveras?',
    'What is his DevOps stack?',
    'What experience does he have?',
    'How can I contact or hire him?',
    'Tell me about GeekClub',
    'Download CV'
  ];

  var toggle = document.getElementById('chatbot-toggle');
  var panel = document.getElementById('chatbot-panel');
  var closeBtn = document.getElementById('chatbot-close');
  var log = document.getElementById('chatbot-log');
  var chipsEl = document.getElementById('chatbot-chips');
  var form = document.getElementById('chatbot-form');
  var input = document.getElementById('chatbot-input');

  if (!toggle || !panel || !closeBtn || !log || !chipsEl || !form || !input) {
    return; // markup missing: bail out silently, never break the page
  }

  // --- Rules engine --------------------------------------------------

  function findRule(text) {
    var lower = text.toLowerCase();
    for (var i = 0; i < FAQ.length; i++) {
      var rule = FAQ[i];
      for (var j = 0; j < rule.keywords.length; j++) {
        if (lower.indexOf(rule.keywords[j]) !== -1) {
          return rule;
        }
      }
    }
    return null;
  }

  // --- Rendering -----------------------------------------------------

  function mailtoHref(userText) {
    var body = userText && userText.trim() ? userText.trim() : MAIL_DEFAULT_BODY;
    return 'mailto:' + EMAIL +
      '?subject=' + encodeURIComponent(MAIL_SUBJECT) +
      '&body=' + encodeURIComponent(body);
  }

  function addMessage(kind, text, withEmail, userText) {
    var row = document.createElement('div');
    row.className = 'chatbot-msg chatbot-msg-' + kind;

    var prefix = document.createElement('span');
    prefix.className = 'chatbot-prefix';
    prefix.textContent = kind === 'user' ? '$ ' : '# ';
    row.appendChild(prefix);

    var body = document.createElement('span');
    body.className = 'chatbot-text';
    body.textContent = text; // textContent: user input is never innerHTML
    row.appendChild(body);

    if (withEmail) {
      var actions = document.createElement('div');
      actions.className = 'chatbot-msg-actions';

      var link = document.createElement('a');
      link.className = 'chatbot-email-btn';
      link.href = mailtoHref(userText);
      link.target = '_blank';
      link.rel = 'noopener';
      link.textContent = 'email ' + EMAIL;
      actions.appendChild(link);

      row.appendChild(actions);
    }

    log.appendChild(row);
    log.scrollTop = log.scrollHeight;
  }

  function sendMessage(raw) {
    var text = (raw || '').trim();
    if (!text) {
      return;
    }

    addMessage('user', text);

    var rule = findRule(text);
    if (rule) {
      addMessage('bot', rule.answer, rule.offerEmail === true, text);
    } else {
      addMessage('bot', FALLBACK, true, text);
    }
  }

  // --- Chips ---------------------------------------------------------

  function renderChips() {
    QUICK_QUESTIONS.forEach(function (q) {
      var chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'chatbot-chip';
      chip.textContent = q;
      chip.addEventListener('click', function () {
        sendMessage(q);
      });
      chipsEl.appendChild(chip);
    });
  }

  function setOpen(open) {
    panel.hidden = !open;
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  // --- Wire up -------------------------------------------------------

  renderChips();
  addMessage('bot', GREETING);

  toggle.addEventListener('click', function () {
    var opening = panel.hidden;
    setOpen(opening);
    if (opening) {
      input.focus();
      log.scrollTop = log.scrollHeight;
    }
  });

  closeBtn.addEventListener('click', function () {
    setOpen(false);
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    sendMessage(input.value);
    input.value = '';
    input.focus();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !panel.hidden) {
      setOpen(false);
      toggle.focus();
    }
  });
})();