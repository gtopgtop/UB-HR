from django.views.generic import TemplateView

from .pages import SECTIONS, crumbs


class PageView(TemplateView):
    """Renders one screen from hr/pages.py inside the shared shell. Touches no database."""

    page = None

    def get_template_names(self):
        return [f"hr/{self.page.template}.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = self.page
        context["crumbs"] = crumbs(self.page)
        context["nav"] = [
            {"section": s, "open": not s.collapsible or self.page in s.pages}
            for s in SECTIONS
        ]
        return context
