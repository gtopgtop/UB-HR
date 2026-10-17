from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .charts import meter, sparkline
from .pages import BY_NAME, PAGES
from .sample_data import DEPTS


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
        self.assertContains(resp, "School average by semester: AY 2024–25 S1 4.0")

    def test_records_totals_add_up(self):
        resp = self.client.get(BY_NAME["records"].url)
        self.assertTemplateUsed(resp, "hr/records.html")
        self.assertContains(resp, "₱5,744,800.00")  # gross on the current payroll run
        self.assertContains(resp, "₱5,170,259.60")  # net: gross minus ₱574,540.40 deductions
        self.assertContains(resp, "₱19,415,454.00")  # remittances, 2026 to date
        self.assertContains(resp, "Showing 8 of 248")  # the directory counts the dashboard's headcount
        self.assertContains(resp, 'data-dialog-open="decline-dialog"', count=4)  # one per pending correction

    def test_government_ids_render_masked(self):
        resp = self.client.get(BY_NAME["records"].url)
        self.assertContains(resp, ">••-•••••••-1</span>")
        self.assertNotContains(resp, ">34-0000000-1<")

    def test_attendance_is_school_wide(self):
        resp = self.client.get(BY_NAME["attendance"].url)
        self.assertTemplateUsed(resp, "hr/attendance.html")
        self.assertContains(resp, "214 of 236 in")  # the same figures as the dashboard
        self.assertContains(resp, "Remind 22 not timed in")
        self.assertContains(resp, "<strong>97.0%</strong>")  # October's tally, before the script redraws it
        self.assertContains(resp, "data-leave-approve", count=9)  # every request waiting at step 2
        self.assertContains(resp, "Enrollment audit that day")

    def test_attendance_calendar_data(self):
        # The month grid is drawn by calendar.js from this JSON (handoff layout, plan §3 Module 2).
        resp = self.client.get(BY_NAME["attendance"].url)
        self.assertContains(resp, '<script id="calendar-data" type="application/json">')
        cal = resp.context["calendar"]
        self.assertEqual((cal["school_year"], cal["today"]), ("2026-2027", "2026-10-12"))
        for ev in cal["events"] + cal["mine"]:
            with self.subTest(event=ev["title"]):
                self.assertLessEqual(ev["start_date"], ev["end_date"])
                self.assertGreaterEqual(ev["start_date"], "2026-07-01")  # inside the school year,
                self.assertLessEqual(ev["end_date"], "2027-06-30")       # July 1 to June 30

        self.assertTrue(cal["can_edit_school"])  # HR keeps the school calendar

        days = cal["attendance"]
        today = days["2026-10-12"]
        self.assertEqual((today["present"], today["not_timed_in"], today["on_leave"]), (214, 22, 12))
        self.assertFalse(any(d["complete"] for d in today["departments"]))  # everyone still has people to come
        self.assertNotIn("2026-08-21", days)  # Ninoy Aquino Day: a holiday is not a work day
        self.assertNotIn("2026-10-10", days)  # a Saturday
        self.assertTrue(all(day <= cal["today"] for day in days))  # nothing recorded ahead of today
        for key, rec in days.items():
            with self.subTest(day=key):
                for field in ("staff", "present", "late", "absent", "on_leave", "not_timed_in"):
                    self.assertEqual(rec[field], sum(d[field] for d in rec["departments"]))
                self.assertEqual(rec["staff"], rec["present"] + rec["absent"] + rec["on_leave"] + rec["not_timed_in"])
        closed = [r for d, r in days.items() if d.startswith("2026-10") and d < cal["today"]]
        self.assertEqual(len(closed), 7)  # Oct 1–2 and 5–9: the days in the tally

    def test_dashboard_totals_add_up_across_departments(self):
        resp = self.client.get(BY_NAME["dashboard"].url)
        self.assertContains(resp, "of 236 expected · 17 late")  # 248 employees less 12 on leave
        self.assertContains(resp, "22 not timed in yet")
        self.assertContains(resp, "<strong>225</strong> of 248")  # evaluators assigned: 9 + 14 still missing
        self.assertContains(resp, "3 waiting over 3 working days")
        self.assertContains(resp, "View all 9")

    def test_sidebar_shows_the_sample_user(self):
        resp = self.client.get(BY_NAME["records"].url)
        self.assertContains(resp, '<div class="ds-user-name">Alex Rivera</div>')
        self.assertContains(resp, '<div class="ds-user-role">HR Officer</div>')

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
        self.assertContains(self.client.get(BY_NAME["career"].url), "<li>Salary grade path</li>")

    def test_wellness_shows_groups_only(self):
        resp = self.client.get(BY_NAME["wellness"].url)
        self.assertTemplateUsed(resp, "hr/wellness.html")
        burnout = {b["name"]: (b["score"], b["level"]) for b in resp.context["burnout"]}
        self.assertEqual(burnout["College of Engineering"], (72, "High"))  # the dashboard's alerts
        self.assertEqual(burnout["Basic Education"], (58, "Watch"))
        headcount = {d["name"]: d["headcount"] for d in DEPTS}
        self.assertTrue(all(headcount[name] >= 5 for name in burnout))  # plan §7.3, rule 1
        self.assertContains(resp, "groups of 5 or more people only")

    def test_messages_and_assistant_follow_the_dashboard(self):
        messages = self.client.get(BY_NAME["messages"].url)
        self.assertTemplateUsed(messages, "hr/messages.html")
        self.assertContains(messages, "Is there anything else HR needs from me?")
        for concern in messages.context["concerns"]:
            self.assertNotIn("name", concern)  # anonymous concerns carry no sender identity
        assistant = self.client.get(BY_NAME["assistant"].url)
        self.assertTemplateUsed(assistant, "hr/assistant.html")
        self.assertContains(assistant, "My payslip is missing the overload pay")
        self.assertContains(assistant, "3 open")

    def test_old_screens_are_gone(self):
        for path in ("/dashboard/", "/admin-dashboard/"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)
