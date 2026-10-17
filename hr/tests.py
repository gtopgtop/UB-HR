from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .charts import meter, sparkline
from .pages import BY_NAME, PAGES


class ChartHelperTests(SimpleTestCase):
    def test_meter_clamps_to_a_percentage(self):
        self.assertEqual(meter(9, 15)["pct"], 60)
        self.assertEqual(meter(3, 0)["pct"], 0)
        self.assertEqual(meter(7, 5)["pct"], 100)

    def test_sparkline_puts_the_highest_value_on_top(self):
        spark = sparkline([("a", 3.9), ("b", 4.4), ("c", 4.1)], height=44, pad=7)
        ys = [dot["y"] for dot in spark["dots"]]
        self.assertEqual(ys[1], 7)
        self.assertEqual(ys[0], 37)
        self.assertEqual(spark["dots"][-1]["x"], 160 - 7)


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
        resp = self.client.get("/")
        self.assertTemplateUsed(resp, "hr/dashboard.html")
        self.assertContains(resp, "Welcome back, Alex")
        self.assertContains(resp, 'aria-current="step"', count=1)
        self.assertContains(resp, "Rating by semester: AY 2024–25 S1 3.9")

    def test_records_totals_add_up(self):
        resp = self.client.get(BY_NAME["records"].url)
        self.assertTemplateUsed(resp, "hr/records.html")
        self.assertContains(resp, "₱25,700.00")  # gross on the latest payslip
        self.assertContains(resp, "₱23,150.10")  # net: gross minus ₱2,549.90 deductions
        self.assertContains(resp, "₱49,749.00")  # contributions and tax, 2026 to date

    def test_government_ids_render_masked(self):
        resp = self.client.get(BY_NAME["records"].url)
        self.assertContains(resp, ">••-•••••••-1</span>")
        self.assertNotContains(resp, ">34-0000000-1<")

    def test_sidebar_shows_the_sample_user(self):
        self.assertContains(self.client.get(BY_NAME["records"].url), '<div class="ds-user-name">Alex Rivera</div>')

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
