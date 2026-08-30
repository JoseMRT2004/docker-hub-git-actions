"""Content regression tests for the DevOps landing page.

If a required element disappears from the page (or an unwanted claim
sneaks back in), these tests fail in CI before any Docker image gets
published. Stdlib only: no HTML parser needed for the checks we make.
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
STYLESHEET = ROOT / "assets" / "css" / "styles.css"
DOCKERFILE = ROOT / "Dockerfile"
WORKFLOW = ROOT / ".github" / "workflows" / "deploy.yml"

HTML = INDEX.read_text(encoding="utf-8")
CSS = STYLESHEET.read_text(encoding="utf-8")
APP_JS = (ROOT / "assets" / "js" / "app.js").read_text(encoding="utf-8")
CHATBOT_JS = (ROOT / "assets" / "js" / "chatbot.js").read_text(encoding="utf-8")
YML = WORKFLOW.read_text(encoding="utf-8")

# Prose assertions run against whitespace-normalized markup so that
# editor formatting (Prettier & friends) can never break them.
HTML_NORM = " ".join(HTML.split())


# --- Branding and hero -------------------------------------------------

def test_title_matches_new_branding():
    assert "<title>Jose M. Taveras — Software Dev. | DevOps</title>" in HTML


def test_hero_shows_name_as_heading():
    assert '<h1 class="hero-name">Jose M. Taveras</h1>' in HTML
    assert "<h1 class=\"hero-name\">DevOps Engineer</h1>" not in HTML


def test_role_line_appends_devops():
    role_line = (
        '<span class="flag">GeekClub Leader</span> '
        '<span class="comment">·</span> <span class="flag">DevOps</span>'
    )
    assert role_line in HTML_NORM


# --- Assets ------------------------------------------------------------

def test_avatar_assets_exist_and_are_referenced():
    base = ROOT / "assets" / "img" / "avatars" / "avatar.jpeg"
    full = ROOT / "assets" / "img" / "avatars" / "avatar-full.jpeg"
    assert base.is_file(), "base avatar missing from repo"
    assert full.is_file(), "full hover avatar missing from repo"
    assert 'src="assets/img/avatars/avatar.jpeg"' in HTML
    assert 'src="assets/img/avatars/avatar-full.jpeg"' in HTML


def test_base_avatar_has_alt_text():
    assert 'alt="Portrait of Jose M. Taveras"' in HTML


def test_hover_swaps_base_for_full_avatar():
    assert ".hero-avatar-wrap:hover .hero-avatar-base {" in CSS
    base_block = CSS.split(".hero-avatar-wrap:hover .hero-avatar-base {")[1].split("}")[0]
    assert "opacity: 0;" in base_block
    full_block = CSS.split(".hero-avatar-wrap:hover .hero-avatar-full {")[1].split("}")[0]
    assert "opacity: 1;" in full_block


def test_all_local_references_resolve():
    refs = re.findall(r'(?:src|href)="([^"]+)"', HTML)
    # Skip external URLs and in-page anchors first, then strip any fragment
    # (e.g. sprite <use href="icons.svg#icon-x">) so the reference resolves
    # to the actual file on disk.
    local = [
        r.split("#")[0]
        for r in refs
        if not r.startswith(("http://", "https://", "#", "mailto:"))
    ]
    assert local, "expected at least one local asset reference"
    for ref in local:
        assert ref, "empty local reference after stripping fragment"
        assert (ROOT / ref).is_file(), f"broken local reference: {ref}"


def test_hero_icon_has_explicit_size():
    # The hero (cv/github) icons render because .icon defines dimensions; a
    # sprite <use> inside an SVG with only a viewBox collapses to zero size
    # without them (the social icons size via .social-item svg instead).
    assert ".icon {" in CSS
    icon_block = CSS.split(".icon {")[1].split("}")[0]
    assert "width" in icon_block and "height" in icon_block


def test_icon_sprite_is_embedded_and_referenced():
    # Icons live in an embedded sprite (renders from file:// and HTTP), not an
    # external .svg file (which breaks in some contexts). Symbols are defined
    # inline and referenced via <use href="#icon-x">.
    assert "assets/img/icons.svg" not in HTML, "external sprite file reference removed"
    for icon in ("icon-github", "icon-linkedin", "icon-email", "icon-download"):
        assert f'<symbol id="{icon}"' in HTML, f"sprite missing symbol: {icon}"
        assert f'href="#{icon}"' in HTML, f"icon not used: {icon}"


def test_no_inline_icon_paths_in_markup():
    # Icon paths are defined exactly once inside the embedded sprite <symbol>s
    # and reused via <use>; they are never duplicated inline at each use site.
    assert HTML.count("6.626 0-12 5.373-12 12 0 5.302") == 1, "octocat path must appear once (sprite symbol)"
    assert HTML.count("20.447 20.452h-3.554") == 1, "linkedin path must appear once"
    assert HTML.count("M20 4H4a2 2") == 1, "email path must appear once (sprite symbol)"
    assert HTML.count('href="#icon-github"') == 2, "github used via <use> (hero + contact)"
    assert HTML.count('href="#icon-linkedin"') == 1
    assert HTML.count('href="#icon-email"') == 1
    assert HTML.count('href="#icon-download"') == 1


# --- CV download -------------------------------------------------------

def test_cv_file_exists_and_is_shipped_by_docker():
    cv = ROOT / "JoseMTaveras_CV.pdf"
    assert cv.is_file(), "CV pdf missing from repo"
    assert cv.stat().st_size > 10_000, "CV pdf looks truncated"
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    assert "COPY JoseMTaveras_CV.pdf" in dockerfile


def test_cv_download_links_are_present():
    count = HTML.count('href="JoseMTaveras_CV.pdf" download')
    assert count >= 3, f"expected CV download links in top bar, hero and footer; found {count}"


# --- Content honesty ----------------------------------------------------

def test_geekclub_member_count_updated():
    assert "90+ member tech community" in HTML_NORM
    assert "73+" not in HTML


def test_unverified_plugin_claim_removed():
    assert "added a plugin for CI workflow automation" not in HTML
    assert "Documented Git-related plugin internals" not in HTML
    assert (
        "Contributed to official documentation: documented prompt "
        "styles and Git-related plugin functions." in HTML_NORM
    )


def test_french_removed_from_experience():
    assert "French" not in HTML


def test_social_links_present():
    for url in (
        "github.com/JoseMRT2004",
        "linkedin.com/in/jose-m-taveras-reyes",
        "mailto:josemtaverasreyes@gmail.com",
    ):
        assert url in HTML


def test_tiktok_removed_from_contact():
    # TikTok was replaced by an Email/mailto contact per the owner's request.
    assert "tiktok.com/@_name_.dev" not in HTML
    assert "icon-tiktok" not in HTML
    assert "TikTok" not in HTML


# --- Separation of concerns ---------------------------------------------

def test_styles_extracted_from_html():
    assert "<style>" not in HTML, "CSS must live in assets/css/styles.css, not inline"
    assert 'href="assets/css/styles.css"' in HTML


def test_behavior_extracted_from_html():
    assert "<script>" not in HTML, "JS must live in assets/js/app.js, not inline"
    assert 'src="assets/js/app.js"' in HTML
    assert "Automating infrastructure..." in APP_JS


# --- i18n ------------------------------------------------------------

I18N_JS = (ROOT / "assets" / "js" / "i18n.js").read_text(encoding="utf-8")


def test_i18n_module_exists_and_is_referenced():
    assert (ROOT / "assets" / "js" / "i18n.js").is_file()
    assert 'src="assets/js/i18n.js"' in HTML


def test_i18n_is_browser_language_detection_not_a_button():
    # This is a browser/system-language preference, not a translate button:
    # there must be no language toggle in the markup, and the detection must
    # read the browser language.
    assert "lang-toggle" not in HTML
    assert "navigator.language" in I18N_JS


def test_i18n_uses_localstorage_persistence():
    assert "localStorage" in I18N_JS


def test_every_data_i18n_key_exists_in_en_and_es():
    keys_in_html = set(re.findall(r'data-i18n="([^"]+)"', HTML))
    assert keys_in_html, "expected at least one data-i18n key in the markup"
    en_block = I18N_JS[I18N_JS.index("en: {"):I18N_JS.index("},")]
    es_block = I18N_JS[I18N_JS.index("es: {"):I18N_JS.index("\n  };")]
    for key in keys_in_html:
        assert f"'{key}'" in en_block, f"missing EN translation for {key}"
        assert f"'{key}'" in es_block, f"missing ES translation for {key}"


def test_i18n_defaults_to_english_markup():
    # The shipped (no-JS / default) content is English.
    assert '<span class="section-label" data-i18n="nav.experience">experience</span>' in HTML
    assert '<span class="section-label" data-i18n="nav.contact">contact</span>' in HTML


# --- Theme (automatic light/dark) -------------------------------------

def test_theme_is_browser_preference_not_a_toggle():
    # Same philosophy as i18n: the theme follows the browser/system preference.
    # There must be no visible theme toggle button in the markup.
    assert "theme-toggle" not in HTML
    assert "themeSwitch" not in HTML


def test_css_detects_system_color_scheme():
    assert "@media (prefers-color-scheme: light)" in CSS


def test_light_block_overrides_key_tokens():
    light = CSS[CSS.index("@media (prefers-color-scheme: light)"):]
    light_block = light[:light.index("}")]
    for token in ("--bg:", "--surface:", "--text:", "--accent:", "--muted:"):
        assert token in light_block, f"light theme missing token override: {token}"


def test_dark_remains_default_fallback():
    # Dark is the identity and the no-media-query fallback (defined in :root).
    root = CSS[CSS.index(":root {"):CSS.index("RESET & BASE")]
    assert "--bg: #0C0C0C" in root


# --- Posts / field notes ----------------------------------------------

POSTS_IMAGES = [
    "assets/img/posts/me-teaching-the-campus.webp",
    "assets/img/posts/news-room.webp",
    "assets/img/posts/semana-global.webp",
    "assets/img/posts/sic-team-photo-1.webp",
]


def test_posts_section_exists():
    assert 'id="posts"' in HTML
    assert 'class="posts-grid"' in HTML


def test_removed_photo_is_not_referenced_or_shipped():
    # The user asked to drop the sic-working-team photo entirely.
    assert "sic-working-team" not in HTML
    assert not (ROOT / "assets/img/posts/sic-working-team.webp").exists()
    assert not (ROOT / "assets/img/posts/sic-working-team.jpg").exists()


def test_all_post_images_are_referenced_and_resolve():
    for img in POSTS_IMAGES:
        assert f'src="{img}"' in HTML, f"post image not referenced: {img}"
        assert (ROOT / img).is_file(), f"post image missing from repo: {img}"


def test_post_images_are_lazy_loaded():
    # Every post image should lazy-load for performance.
    for img in POSTS_IMAGES:
        idx = HTML.index(f'src="{img}"')
        # collect the full <img ...> tag and check it carries loading="lazy"
        before = HTML[:idx]
        tag_start = before.rindex("<img")
        tag_end = HTML.index(">", idx)
        tag = HTML[tag_start:tag_end]
        assert 'loading="lazy"' in tag, f"not lazy-loaded: {img}"


def test_posts_grid_uses_16_9_frames():
    assert "aspect-ratio: 16 / 9" in CSS
    assert "object-fit: cover" in CSS


def test_posts_enter_from_directed_sides_with_stagger():
    # Each post animates in from a direction and the grid staggers the reveal.
    for var in ("post-item--left", "post-item--right", "post-item--up"):
        assert var in HTML_NORM, f"missing directed entry variant: {var}"
        assert CSS.split(var)[1].split("}")[0].strip(), f"{var} has no styles"
    # laid out in the grid (class present on post items)
    assert HTML_NORM.count("post-item--") >= 4
    # stagger via nth-child transition-delay in the stylesheet
    assert ":nth-child(1) { transition-delay: 0.00s" in CSS
    assert ":nth-child(4) { transition-delay: 0.36s" in CSS


def test_post_hover_focus_blurs_others_and_keys_hovered():
    # Hover "focus": hovering the grid blurs all photos; the hovered one snaps
    # back sharp with the avatar-pulse glow on its frame.
    grid_hover = CSS.split(".posts-grid:hover .post-img")[1].split("}")[0]
    assert "blur(4px)" in grid_hover
    active = CSS.split(".posts-grid:hover .post-item:hover .post-img")[1].split("}")[0]
    assert "blur(0)" in active and "scale(" in active
    hover_frame = CSS.split(".post-item:hover .post-frame")[1].split("}")[0]
    assert "box-shadow" in hover_frame and "avatar-pulse" in hover_frame
    assert "avatar-pulse" in CSS


def test_large_source_photo_has_compact_webp():
    # The 3MB source JPG becomes a small WebP for the page.
    webp = ROOT / "assets" / "img" / "posts" / "sic-team-photo-1.webp"
    assert webp.is_file()
    assert webp.stat().st_size < 500_000, "WebP should be far smaller than the 3MB source"


def test_dom_balance():
    opens = HTML.count("<div")
    closes = HTML.count("</div>")
    assert opens == closes, f"div mismatch: {opens} opens, {closes} closes"


def test_section_order_experience_before_skills():
    # "Primero la experiencia": experience must appear right after the hero,
    # before skills. Assert by index in the markup.
    hero = HTML.index("id=\"hero\"") if "id=\"hero\"" in HTML else HTML.index("hero-name")
    exp = HTML.index("id=\"experience\"")
    skills = HTML.index("id=\"skills\"")
    certs = HTML.index("id=\"certifications\"")
    posts = HTML.index("id=\"posts\"")
    contact = HTML.index("id=\"contact\"")
    assert hero < exp < skills < certs < posts < contact
    # nav order matches too
    assert HTML.index("href=\"#experience\"") < HTML.index("href=\"#skills\"")
    assert HTML.index("href=\"#skills\"") < HTML.index("href=\"#certifications\"") < HTML.index("href=\"#contact\"")


def test_favicon_references_avatar_icon():
    assert 'rel="icon"' in HTML
    assert 'href="assets/img/options/avatar-icon.webp"' in HTML
    assert 'type="image/webp"' in HTML
    assert (ROOT / "assets" / "img" / "options" / "avatar-icon.webp").is_file()


# --- Certifications -----------------------------------------------------

CERTS_IMAGES = [
    "assets/img/certs/samsung.webp",
    "assets/img/certs/python-essentials.webp",
    "assets/img/certs/pre-security.webp",
    "assets/img/certs/it-essentials.webp",
    "assets/img/certs/ethical-hacking.webp",
    "assets/img/certs/linux.webp",
    "assets/img/certs/os-basics.webp",
    "assets/img/certs/microsoft-learn.webp",
    "assets/img/certs/plan-agile.webp",
    "assets/img/certs/branch-strategies.webp",
    "assets/img/certs/manage-repositories.webp",
]


def test_certifications_section_exists():
    assert 'id="certifications"' in HTML
    assert "certs-grid" in HTML
    assert HTML.count("cert-item") >= 8


def test_all_cert_images_referenced_and_resolve():
    for img in CERTS_IMAGES:
        assert f'src="{img}"' in HTML, f"cert image not referenced: {img}"
        assert (ROOT / img).is_file(), f"cert image missing from repo: {img}"


def test_cert_images_are_lazy_loaded():
    for img in CERTS_IMAGES:
        idx = HTML.index(f'src="{img}"')
        before = HTML[:idx]
        tag_start = before.rindex("<img")
        tag_end = HTML.index(">", idx)
        tag = HTML[tag_start:tag_end]
        assert 'loading="lazy"' in tag, f"not lazy-loaded: {img}"


def test_cert_hover_focus_grows_hovered_card():
    # Hovering the grid blurs neighbours; the hovered cert snaps back sharp,
    # and a large floating preview renders the certificate at "photo size".
    grid_hover = CSS.split(".certs-grid:hover .cert-item img")[1].split("}")[0]
    assert "blur(1.5px)" in grid_hover
    active = CSS.split(".certs-grid:hover .cert-item:hover img")[1].split("}")[0]
    assert "blur(0)" in active and "scale(" in active
    # A floating preview shows the full cert at photo size on hover.
    assert ".cert-preview" in CSS
    assert ".cert-item:hover .cert-preview" in CSS
    assert "cert-preview-img" in HTML


def test_ms_certificates_spin_clockwise_on_hover():
    # Microsoft Learn certs spin a full clockwise (360°) circle on hover.
    assert '.cert-item[data-cert-name^="cert.ms_"]:hover img' in CSS
    assert "@keyframes certMsSpin" in CSS
    assert "rotate(360deg)" in CSS


def test_snake_pointer_points_at_chatbot():
    # The "serpentine" pointer is fixed, curls toward the chat bubble and
    # carries a small "pregúntame" tag sized to half the chatbot's "#".
    assert 'class="cert-pointer"' in HTML
    assert 'class="cert-pointer-snake"' in HTML
    assert 'class="snake-path"' in HTML
    assert 'class="snake-arrow"' in HTML
    assert "pregúntame" in HTML
    assert "cert-pointer-tag" in CSS
    # fixed toward the chat bubble (bottom-right)
    assert "position: fixed" in CSS.split(".cert-pointer {")[1].split("}")[0]
    # tag font-size is half of the chatbot prompt's 0.8rem
    assert "font-size: 0.4rem" in CSS.split(".cert-pointer-tag")[1].split("}")[0]


def test_cert_i18n_keys_present():
    for key in ("nav.certifications", "cert.label", "cert.samsung", "cert.cisco_python",
                "cert.ms_agile", "cert.ms_branch", "cert.ms_repos", "cert.ms_learn"):
        assert f'data-i18n="{key}"' in HTML or f"'{key}'" in I18N_JS, f"missing i18n key: {key}"


def test_stylesheet_keeps_design_tokens_and_is_pruned():
    assert ":root {" in CSS and "--accent:" in CSS
    assert ".prompt {" not in CSS
    assert ".string {" not in CSS


# --- FAQ chatbot -------------------------------------------------

def test_chatbot_script_exists_and_is_referenced():
    assert (ROOT / "assets" / "js" / "chatbot.js").is_file()
    assert 'src="assets/js/chatbot.js"' in HTML


def test_chatbot_markup_present():
    assert 'id="chatbot-toggle"' in HTML
    assert 'id="chatbot-panel"' in HTML
    assert 'id="chatbot-log"' in HTML
    assert 'id="chatbot-input"' in HTML
    assert 'id="chatbot-close"' in HTML


def test_chatbot_script_has_rules_and_mailto_fallback():
    assert "FAQ" in CHATBOT_JS
    assert "keywords" in CHATBOT_JS
    assert "mailto:" in CHATBOT_JS
    assert "josemtaverasreyes@gmail.com" in CHATBOT_JS


def test_chatbot_has_at_least_six_faq_rules():
    assert CHATBOT_JS.count("keywords: [") >= 6


def test_chatbot_answers_use_structured_bullets():
    # "Formato más entendible": several rules render bullet lists, which are
    # built as nodes (textContent), never innerHTML.
    assert CHATBOT_JS.count("items: [") >= 3
    assert "chatbot-bullets" in CHATBOT_JS
    assert "document.createElement('ul')" in CHATBOT_JS
    assert "li.textContent = item" in CHATBOT_JS
    # Never assign innerHTML (comments may mention the word; the code must not
    # use it to inject user input).
    assert "innerHTML =" not in CHATBOT_JS


def test_chatbot_bullet_styles_use_palette():
    assert ".chatbot-bullets li::before {" in CSS
    assert "var(--cyan)" in CSS
    assert "var(--accent)" in CSS


def test_chatbot_styles_use_design_tokens():
    assert ".chatbot-toggle {" in CSS
    assert ".chatbot-panel {" in CSS
    assert "z-index: 9000" in CSS
    assert "var(--accent)" in CSS
    assert "var(--surface)" in CSS


# --- Pipeline ------------------------------------------------------------

def test_dockerfile_ships_static_assets():
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    assert "COPY assets/ /usr/share/nginx/html/assets/" in dockerfile
    assert "COPY index.html /usr/share/nginx/html/" in dockerfile


def test_workflow_runs_tests_before_docker_build():
    assert "uv run pytest" in YML
    assert "needs: test" in YML


def test_workflow_runs_tests_on_pull_requests():
    # Every PR to main must run the test job, so reviewers get CI feedback.
    assert "pull_request:" in YML
    assert "branches: [main]" in YML


def test_workflow_never_deploys_from_a_pull_request():
    # on: triggers are workflow-level; per-job if: guards are what stop PRs
    # from pushing Docker images or deploying Render. Re-adding pull_request
    # without these guards would expose secrets and deploy on every branch PR.
    assert "if: github.event_name == 'push'" in YML
    # guards must protect BOTH the build and the deploy job.
    deploy_block = YML[YML.index("deploy-render:"):]
    assert "if: github.event_name == 'push'" in deploy_block
    # deploy must never run without a build, so no image ever skips the chain.
    assert "deploy-render:\n    needs: build-and-push" in YML
