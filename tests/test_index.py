import re
from pathlib import Path
import pytest


# ============================================================
# PROJECT FILES
# ============================================================

ROOT = Path(".")
HTML_PATH = ROOT / "index.html"
CSS_PATH = ROOT / "assets/css/styles.css"

HTML = HTML_PATH.read_text(encoding="utf-8")
CSS = CSS_PATH.read_text(encoding="utf-8")


# ============================================================
# HELPERS
# ============================================================

def workflows():
    return list(Path(".github/workflows").glob("*.yml")) + list(
        Path(".github/workflows").glob("*.yaml")
    )


def img_tags():
    return re.findall(
        r"<img\b[^>]*>",
        HTML,
        re.IGNORECASE | re.DOTALL,
    )


def local_assets():
    assets = re.findall(
        r'(?:src|href)=[\'"]([^\'"]+)[\'"]',
        HTML,
        re.IGNORECASE,
    )

    return [
        asset
        for asset in assets
        if not asset.startswith(
            ("http://", "https://", "//", "data:", "#", "mailto:")
        )
        and not asset.startswith("javascript:")
    ]


# ============================================================
# 1. HTML
# ============================================================

def test_html_exists():
    assert HTML_PATH.exists()


def test_html_has_basic_document_structure():
    assert re.search(r"<!doctype html>", HTML, re.IGNORECASE)
    assert re.search(r"<html\b", HTML, re.IGNORECASE)
    assert re.search(r"<head\b", HTML, re.IGNORECASE)
    assert re.search(r"<body\b", HTML, re.IGNORECASE)
    assert re.search(r"</html>", HTML, re.IGNORECASE)


def test_html_language_is_defined():
    assert re.search(
        r'<html\b[^>]*\blang=[\'"][^\'"]+[\'"]',
        HTML,
        re.IGNORECASE,
    )


def test_page_has_title():
    match = re.search(
        r"<title>(.*?)</title>",
        HTML,
        re.IGNORECASE | re.DOTALL,
    )

    assert match
    assert match.group(1).strip()


# ============================================================
# 2. ASSETS
# ============================================================

def test_stylesheet_exists():
    assert CSS_PATH.exists()


def test_local_asset_references_exist():
    ignored_extensions = {".html", ".htm"}

    for reference in local_assets():
        clean_reference = reference.split("?", 1)[0].split("#", 1)[0]

        if not clean_reference:
            continue

        path = Path(clean_reference)

        if path.suffix.lower() in ignored_extensions:
            continue

        assert path.exists(), f"Broken local asset reference: {reference}"


# ============================================================
# 3. ACCESSIBILITY
# ============================================================

def test_images_have_alt_attributes():
    for tag in img_tags():
        assert re.search(
            r'\balt=[\'"][^\'"]*[\'"]',
            tag,
            re.IGNORECASE,
        ), f"Image missing alt attribute: {tag}"


def test_links_have_non_empty_href():
    links = re.findall(
        r"<a\b[^>]*\bhref=[\"']([^\"']*)[\"']",
        HTML,
        re.IGNORECASE | re.DOTALL,
    )

    for href in links:
        assert href.strip()


# ============================================================
# 4. JAVASCRIPT
# ============================================================

def test_javascript_files_exist():
    scripts = re.findall(
        r'<script\b[^>]*\bsrc=[\'"]([^\'"]+\.js)[\'"]',
        HTML,
        re.IGNORECASE,
    )

    for src in scripts:
        assert Path(src).exists(), f"Missing JavaScript file: {src}"


# ============================================================
# 5. CV
# ============================================================

def test_cv_link_points_to_existing_file():
    cv_links = re.findall(
        r'<a\b[^>]*href=[\'"]([^\'"]+\.pdf)[\'"]',
        HTML,
        re.IGNORECASE,
    )

    for href in cv_links:
        path = Path(href.split("?", 1)[0].split("#", 1)[0])
        assert path.exists(), f"Linked PDF does not exist: {href}"


# ============================================================
# 6. CI / CD
# ============================================================

def test_ci_workflow_exists():
    assert workflows(), "No GitHub Actions workflow found"


def test_ci_runs_tests():
    content = "\n".join(
        workflow.read_text(encoding="utf-8")
        for workflow in workflows()
    )

    assert re.search(
        r"\bpytest\b",
        content,
        re.IGNORECASE,
    ), "CI workflow does not appear to run pytest"


def test_ci_builds_docker_image_when_dockerfile_exists():
    if not Path("Dockerfile").exists():
        pytest.skip("No Dockerfile; Docker build is not applicable")

    content = "\n".join(
        workflow.read_text(encoding="utf-8")
        for workflow in workflows()
    )

    docker_build = re.search(
        r"\bdocker\s+build\b",
        content,
        re.IGNORECASE,
    )

    docker_action = re.search(
        r"docker/build-push-action@",
        content,
        re.IGNORECASE,
    )

    assert docker_build or docker_action, (
        "CI workflow does not appear to build the Docker image"
    )