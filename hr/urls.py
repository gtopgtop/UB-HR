from django.urls import path

from .pages import PAGES
from .views import PageView, view_as

app_name = "hr"

urlpatterns = [path(page.path, PageView.as_view(page=page), name=page.name) for page in PAGES] + [
    path("view-as/", view_as, name="view_as"),
]
