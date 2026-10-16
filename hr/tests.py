from django.test import TestCase
from django.urls import reverse

# Each screen and one piece of text that proves the right template rendered.
SCREENS = {
    "employee_home": "Welcome back, [First name]",
    "wellness": "Share a concern",
    "admin_dashboard": "Pending leave requests",
    "employee_dashboard": "Prof. Maria L. Reyes",
}


class StaticScreenTests(TestCase):
    def test_every_screen_renders(self):
        for name, marker in SCREENS.items():
            with self.subTest(screen=name):
                resp = self.client.get(reverse(f"hr:{name}"))
                self.assertContains(resp, marker)

    def test_screens_do_not_query_the_database(self):
        for name in SCREENS:
            with self.subTest(screen=name), self.assertNumQueries(0):
                self.client.get(reverse(f"hr:{name}"))

    def test_nav_highlights_current_section(self):
        self.assertContains(self.client.get(reverse("hr:wellness")), 'href="/wellness/" class="is-active"')
        self.assertContains(self.client.get(reverse("hr:employee_home")), 'class="is-active">Home')
