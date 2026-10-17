from django.test import TestCase
from django.urls import reverse

from .pages import BY_NAME, PAGES


class ShellTests(TestCase):
    def test_every_page_renders_in_the_shell(self):
        for page in PAGES:
            with self.subTest(page=page.name):
                resp = self.client.get(page.url)
                self.assertContains(resp, f'<h1 class="ds-page-title">{page.title}</h1>', html=False)
                self.assertContains(resp, 'aria-label="Main navigation"')

    def test_pages_do_not_query_the_database(self):
        for page in PAGES:
            with self.subTest(page=page.name), self.assertNumQueries(0):
                self.client.get(page.url)

    def test_dashboard_is_the_landing_page(self):
        self.assertEqual(reverse("hr:dashboard"), "/")
        self.assertTemplateUsed(self.client.get("/"), "hr/dashboard.html")

    def test_nav_marks_only_the_current_page(self):
        resp = self.client.get(BY_NAME["wellness"].url)
        self.assertContains(resp, 'href="/wellness/" aria-current="page"', count=1)
        self.assertContains(resp, 'aria-current="page"', count=1)

    def test_collapsible_group_opens_when_it_holds_the_current_page(self):
        closed = self.client.get(BY_NAME["dashboard"].url).content.decode()
        opened = self.client.get(BY_NAME["breakdown"].url).content.decode()
        self.assertIn('>Career<', closed)
        self.assertIn('aria-expanded="false" aria-controls="nav-2"', closed)
        self.assertIn('aria-expanded="true" aria-controls="nav-2"', opened)

    def test_breadcrumbs_follow_the_parent_chain(self):
        resp = self.client.get(BY_NAME["breakdown"].url)
        self.assertContains(resp, '<a href="/career/">Career progress</a>')
        self.assertContains(resp, '<a href="/career/evaluations/">Evaluations</a>')
        self.assertContains(resp, '<span aria-current="page">Evaluation breakdown</span>')

    def test_placeholder_lists_what_is_planned(self):
        self.assertContains(self.client.get(BY_NAME["attendance"].url), "<li>DTR calendar</li>")

    def test_old_screens_are_gone(self):
        for path in ("/dashboard/", "/admin-dashboard/"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)
