from pathlib import Path

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def asset(path):
    """The static URL with ?v=<last modified>, so the browser fetches a CSS, JS or image file again whenever it
    changes instead of reusing a stale copy (a stale bundle.css loses the project's icons)."""
    found = finders.find(path)
    version = int(Path(found).stat().st_mtime) if found else 0
    return f"{static(path)}?v={version}"
