from django.urls import path
from django.views.generic import TemplateView

app_name = "hr"


def page(template, nav=None):
    """Static page: renders a template, touches no database."""
    return TemplateView.as_view(template_name=f"hr/{template}.html", extra_context={"nav": nav})


urlpatterns = [
    path("", page("employee_home", nav="home"), name="employee_home"),
    path("wellness/", page("wellness", nav="wellness"), name="wellness"),
    path("admin-dashboard/", page("admin_dashboard"), name="admin_dashboard"),
    path("dashboard/", page("employee_dashboard", nav="home"), name="employee_dashboard"),
]
