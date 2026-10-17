from django.urls import path

from .pages import PAGES
from .views import PageView

app_name = "hr"

urlpatterns = [path(page.path, PageView.as_view(page=page), name=page.name) for page in PAGES]
