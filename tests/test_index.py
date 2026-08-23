"""Content regression tests for the DevOps landing page.

If a required element disappears from the page (or an unwanted claim
sneaks back in), these tests fail in CI before any Docker image gets
published.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
DOCKERFILE = ROOT / "Dockerfile"
WORKFLOW = ROOT / ".github" / "workflows" / "deploy.yml"

HTML = INDEX.read_text(encoding="utf-8")
YML = WORKFLOW.read_text(encoding="utf-8")


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
    assert role_line in HTML


def test_avatar_assets_exist_and_are_referenced():
    base = ROOT / "assets" / "avatar.png"
    full = ROOT / "assets" / "avatar-full.png"
    assert base.is_file(), "base avatar missing from repo"
    assert full.is_file(), "full hover avatar missing from repo"
    assert 'src="assets/avatar.png"' in HTML
    assert 'src="assets/avatar-full.png"' in HTML


def test_hover_swaps_base_for_full_avatar():
    assert ".hero-avatar-wrap:hover .hero-avatar-base {" in HTML
    assert "opacity: 0;" in HTML.split(".hero-avatar-wrap:hover .hero-avatar-base {")[1].split("}")[0]
    full_block = HTML.split(".hero-avatar-wrap:hover .hero-avatar-full {")[1].split("}")[0]
    assert "opacity: 1;" in full_block


def test_geekclub_member_count_updated():
    assert "90+ member tech community" in HTML
    assert "73+" not in HTML


def test_unverified_plugin_claim_removed():
    assert "added a plugin for CI workflow automation" not in HTML
    assert "Documented Git-related plugin internals" not in HTML
    assert (
        "Contributed to official documentation: documented prompt "
        "styles and Git-related plugin functions." in HTML
    )


def test_french_removed_from_experience():
    assert "French" not in HTML


def test_cv_remains_downloadable():
    assert "JoseMTaveras_CV.pdf" in HTML


def test_dead_css_classes_pruned():
    assert ".prompt {" not in HTML
    assert ".string {" not in HTML


def test_dockerfile_serves_avatar_assets():
    assert "COPY assets/ /usr/share/nginx/html/assets/" in DOCKERFILE.read_text(
        encoding="utf-8"
    )


def test_workflow_runs_tests_before_docker_build():
    assert "uv run pytest" in YML
    assert "needs: test" in YML
