import os
import re
import pytest

def test_index_html_wcag_accessibility_markers():
    """Verify that key WCAG 2.1 AA accessibility markers exist in the index.html template."""
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "app", "templates", "index.html"
    )
    
    assert os.path.exists(template_path), "index.html template is missing."
    
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    # 1. HTML lang attribute exists
    assert re.search(r"<html\s+[^>]*lang=", html), "index.html does not declare html lang attribute."
    
    # 2. Skip to Content link exists
    assert "skip-link" in html, "index.html is missing a Skip to Content shortcut link."
    assert "main-content" in html, "index.html is missing main-content skip target ID."
    
    # 3. Single h1 heading exists
    h1_count = len(re.findall(r"<h1\b", html))
    assert h1_count == 1, f"index.html must have exactly one <h1> heading (found {h1_count})."
    
    # 4. Aria live landmarks present
    assert "aria-live=" in html, "index.html is missing aria-live screen reader announcer."
    
    # 5. Label connections exist
    assert "<label for=" in html, "index.html is missing form control labels."
