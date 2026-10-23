from django.shortcuts import redirect
from django.views.generic import TemplateView

from . import sample_data
from .pages import BY_NAME, PAGES, ROLE_COOKIE, ROLES, crumbs, nav_for, role_of


class PageView(TemplateView):
    """Renders one screen from hr/pages.py inside the shared shell. Touches no database.

    A page the current role may not open (plan §7.4) shows a no-access notice instead, and the HR
    landing page sends any other role to its own landing.
    """

    page = None

    def get(self, request, *args, **kwargs):
        self.role = role_of(request)
        if self.role.key in self.page.roles:
            return super().get(request, *args, **kwargs)
        if self.page.name == "dashboard":
            return redirect(BY_NAME[self.role.landing].url)
        context = self.shell_context()
        context.update(allowed=[ROLES[key] for key in self.page.roles], landing=BY_NAME[self.role.landing])
        return self.response_class(request, ["hr/no_access.html"], context, status=403)

    def get_template_names(self):
        return [f"hr/{self.page.template}.html"]

    def shell_context(self):
        return {"page": self.page, "crumbs": [], "nav": nav_for(self.role, self.page), "role": self.role,
                "roles": ROLES.values(), "current_user": sample_data.ROLE_USERS[self.role.key]}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.shell_context(), crumbs=crumbs(self.page))
        context.update(sample_data.for_page(self.page.name, self.role.key))
        return context


def view_as(request):
    """The "View as" switcher (plan §9.1): remember the role and open its landing page, or `next` when that
    is a screen the role may open (only known screens, so it cannot redirect anywhere else)."""
    role = ROLES.get(request.GET.get("role", ""), ROLES["hr"])
    target = next((p for p in PAGES if p.url == request.GET.get("next")), None)
    response = redirect(target.url if target and role.key in target.roles else BY_NAME[role.landing].url)
    response.set_cookie(ROLE_COOKIE, role.key, samesite="Lax")
    return response
