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
    local = [r for r in refs if not r.startswith(("http://", "https://", "#"))]
    assert local, "expected at least one local asset reference"
    for ref in local:
        assert (ROOT / ref).is_file(), f"broken local reference: {ref}"


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
        "tiktok.com/@_name_.dev",
    ):
        assert url in HTML


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


def test_dom_balance():
    opens = HTML.count("<div")
    closes = HTML.count("</div>")
    assert opens == closes, f"div mismatch: {opens} opens, {closes} closes"


def test_favicon_references_avatar_option():
    assert 'rel="icon"' in HTML
    assert 'href="assets/img/options/avatar-option.png"' in HTML
    assert (ROOT / "assets" / "img" / "options" / "avatar-option.png").is_file()


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
    assert "mrtaveras.19@gmail.com" in CHATBOT_JS


def test_chatbot_has_at_least_six_faq_rules():
    assert CHATBOT_JS.count("keywords: [") >= 6


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
