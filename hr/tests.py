import re
from pathlib import Path

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .charts import meter, sparkline
from .pages import BY_NAME, DEFAULT_ROLE, PAGES, ROLE_COOKIE, ROLES
from .sample_data import (CONSENTED, DEPT_STRESS, DEPTS, FAQ_ANSWERS, HANDOFFS, PROMOTION_READY, SCHOOL, STAGNANT,
                          STRESS_WEEKS, SURVEY_RESPONSES, THREADS, WELLNESS)


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
    def open(self, page, role=None):
        """GET a page as `role`, or as the HR officer, or else as the first role allowed to open it."""
        self.client.cookies[ROLE_COOKIE] = role or (DEFAULT_ROLE if DEFAULT_ROLE in page.roles else page.roles[0])
        return self.client.get(page.url)

    def test_every_page_renders_in_the_shell(self):
        for page in PAGES:
            with self.subTest(page=page.name):
                resp = self.open(page)
                self.assertContains(resp, f'<h1 class="ds-page-title">{page.title}</h1>', html=False)
                self.assertContains(resp, 'aria-label="Main navigation"')

    def test_pages_do_not_query_the_database(self):
        for page in PAGES:
            with self.subTest(page=page.name), self.assertNumQueries(0):
                self.open(page)

    def test_dashboard_is_the_landing_page(self):
        self.assertEqual(reverse("hr:dashboard"), "/")
        resp = self.client.get("/")
        self.assertTemplateUsed(resp, "hr/dashboard.html")
        self.assertContains(resp, "Welcome back, Alex")
        self.assertContains(resp, 'aria-current="step"', count=1)
        self.assertContains(resp, "School average by semester: AY 2024–25 S1 4.0")

    def test_records_totals_add_up(self):
        resp = self.open(BY_NAME["records"])
        self.assertTemplateUsed(resp, "hr/records.html")
        self.assertContains(resp, "₱5,744,800.00")  # gross on the current payroll run
        self.assertContains(resp, "₱5,170,259.60")  # net: gross minus ₱574,540.40 deductions
        self.assertContains(resp, "₱19,415,454.00")  # remittances, 2026 to date
        self.assertContains(resp, "Showing 8 of 248")  # the directory counts the dashboard's headcount
        self.assertContains(resp, 'data-dialog-open="decline-dialog"', count=4)  # one per pending correction

    def test_government_ids_render_masked(self):
        resp = self.open(BY_NAME["records"])
        self.assertContains(resp, ">••-•••••••-1</span>")
        self.assertNotContains(resp, ">34-0000000-1<")

    def test_attendance_is_school_wide(self):
        resp = self.open(BY_NAME["attendance"])
        self.assertTemplateUsed(resp, "hr/attendance.html")
        self.assertContains(resp, "214 of 236 in")  # the same figures as the dashboard
        self.assertContains(resp, "Remind 22 not timed in")
        self.assertContains(resp, "<strong>96.5%</strong>")  # October's tally, before the script redraws it
        self.assertContains(resp, "data-leave-approve", count=9)  # every request waiting at step 2
        self.assertContains(resp, "Enrollment audit that day")

    def test_attendance_calendar_data(self):
        # The month grid is drawn by calendar.js from this JSON (handoff layout, plan §3 Module 2).
        resp = self.open(BY_NAME["attendance"])
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
        resp = self.open(BY_NAME["dashboard"])
        self.assertContains(resp, "of 236 expected · 17 late")  # 248 employees less 12 on leave
        self.assertContains(resp, "22 not timed in yet")
        self.assertContains(resp, "<strong>225</strong> of 248")  # evaluators assigned: 9 + 14 still missing
        self.assertContains(resp, "3 waiting over 3 working days")
        self.assertContains(resp, "View all 9")

    def test_sidebar_shows_the_sample_user(self):
        resp = self.open(BY_NAME["records"])
        self.assertContains(resp, '<div class="ds-user-name">Alex Rivera</div>')
        self.assertContains(resp, '<div class="ds-user-role">HR Officer</div>')

    def test_nav_marks_only_the_current_page(self):
        resp = self.open(BY_NAME["wellness"])
        self.assertContains(resp, 'href="/wellness/" aria-current="page"', count=1)
        self.assertContains(resp, 'aria-current="page"', count=1)

    def test_collapsible_group_opens_when_it_holds_the_current_page(self):
        closed = self.open(BY_NAME["dashboard"]).content.decode()
        opened = self.open(BY_NAME["breakdown"]).content.decode()
        self.assertIn('>Career<', closed)
        self.assertIn('aria-expanded="false" aria-controls="nav-2"', closed)
        self.assertIn('aria-expanded="true" aria-controls="nav-2"', opened)

    def test_breadcrumbs_follow_the_parent_chain(self):
        resp = self.open(BY_NAME["breakdown"])
        self.assertContains(resp, '<a href="/career/">Career progress</a>')
        self.assertContains(resp, '<a href="/career/evaluations/">Evaluations</a>')
        self.assertContains(resp, '<span aria-current="page">Evaluation breakdown</span>')

    def test_executive_shows_aggregates_only(self):
        resp = self.open(BY_NAME["executive"])
        self.assertTemplateUsed(resp, "hr/executive.html")
        self.assertContains(resp, "most in College of Arts and Sciences (3)")  # plan §10, task 15: one clear answer
        self.assertEqual(resp.context["pipeline_ready"], len(PROMOTION_READY))
        for person in PROMOTION_READY:
            self.assertNotContains(resp, person["name"])  # plan §7.3, rule 6: no drill-down to individuals
        self.assertContains(resp, "Executive view.")

    def test_wellness_office_heatmap_matches_the_school_trend(self):
        resp = self.open(BY_NAME["wellness_office"])
        self.assertTemplateUsed(resp, "hr/wellness_office.html")
        headcount = {d["name"]: d["headcount"] for d in DEPTS}
        for week, (label, school) in enumerate(STRESS_WEEKS):
            with self.subTest(week=label):
                mean = sum(headcount[r["name"]] * r["cells"][week]["value"] for r in resp.context["heat"]) / 248
                self.assertAlmostEqual(mean, school, delta=0.05)
        self.assertEqual([c["days_left"] for c in CONSENTED], [69, 48, 6, 50])  # 90 days from each grant
        self.assertEqual([c["expiring"] for c in resp.context["consented"]], [False, False, True, False])
        self.assertContains(resp, ">Schedule</button>", count=2)  # only the new counselor requests
        self.assertContains(resp, " is-exam", count=len(DEPTS) + 1)  # the prelims week, every row and the school

    def test_settings_weights_add_up(self):
        resp = self.open(BY_NAME["settings"])
        self.assertTemplateUsed(resp, "hr/settings.html")
        for model in resp.context["weight_models"]:
            with self.subTest(model=model["key"]):
                self.assertEqual(model["weights"]["total"], 100)
        self.assertContains(resp, "data-weight ", count=11)  # 6 burnout factors, 5 retention factors
        self.assertContains(resp, '<th scope="row">', count=27)  # every row of the plan §7.4 matrix
        self.assertContains(resp, 'id="rule-5" type="number" min="1" value="3"')  # the leave wait limit

    def test_account_shows_own_roles(self):
        resp = self.open(BY_NAME["account"])
        self.assertTemplateUsed(resp, "hr/account.html")
        self.assertContains(resp, "since Jun 3, 2024 · granted by Corin Abella")
        self.assertContains(resp, 'type="checkbox"', count=13)  # 6 events × 2 channels, plus the sidebar option

    def test_department_pages_show_engineering(self):
        overview = self.open(BY_NAME["department"])
        self.assertContains(overview, "College of Engineering · Dean Ellis Ramirez")
        self.assertContains(overview, "32 of 36 present")  # the dashboard's department figures
        self.assertEqual(overview.context["burnout"]["score"], 72)
        approvals = self.open(BY_NAME["approvals"])
        self.assertContains(approvals, "data-say=", count=approvals.context["overdue"])  # remind only the late ones
        team = self.open(BY_NAME["team"])
        self.assertEqual(len(team.context["team"]), 10)

    def test_hr_dashboard_draws_a_chart_set_per_department(self):
        resp = self.open(BY_NAME["hr_dashboard"])
        self.assertContains(resp, "data-chart-set=", count=8)  # whole school plus 7 departments
        self.assertContains(resp, 'data-chart-set="d0" hidden')
        for r in resp.context["retention"]:
            with self.subTest(department=r["name"]):
                self.assertEqual(r["total"], next(d["headcount"] for d in DEPTS if d["name"] == r["name"]))

    def test_hr_office_pages_follow_the_queues(self):
        leave = self.open(BY_NAME["leave_processing"])
        self.assertContains(leave, "data-leave-approve", count=9)  # the dashboard's "Leave to process"
        requests = self.open(BY_NAME["computation_requests"])
        self.assertContains(requests, "Review and release", count=3)
        self.assertContains(requests, ">Resolve</a>", count=1)
        alerts = self.open(BY_NAME["alerts"])
        self.assertEqual(alerts.context["focus"]["score"], 72)
        self.assertEqual(alerts.context["retention"]["score"], 74)  # High: plan §5.2 factors, no wellness data
        self.assertContains(alerts, "Start an intervention", count=3)  # two buttons and the dialog title
        directory = self.open(BY_NAME["directory"])
        self.assertContains(directory, "data-dir-row", count=len(directory.context["rows"]))
        comms = self.open(BY_NAME["communications"])
        self.assertContains(comms, "201 of 248 acknowledged")  # the dashboard memo's read count

    def test_career_counts_add_up(self):
        resp = self.open(BY_NAME["career"])
        self.assertTemplateUsed(resp, "hr/career.html")
        self.assertEqual(sum(t["headcount"] for t in resp.context["tracks"]), 248)  # every employee on a ladder
        self.assertEqual(resp.context["pipeline_ready"], len(resp.context["ready"]))  # the bars match the list
        self.assertEqual(sum(g["value"] for g in resp.context["salary_grades"]), 248)
        self.assertContains(resp, "Stagnant")

    def test_evaluations_match_the_dashboard(self):
        resp = self.open(BY_NAME["evaluations"])
        self.assertTemplateUsed(resp, "hr/evaluations.html")
        self.assertEqual(resp.context["school_overall"], "4.20")  # the dashboard's school average, 4.2
        self.assertContains(resp, 'aria-current="step"', count=1)
        self.assertContains(resp, "<strong>225</strong> of 248")

    def test_breakdown_combines_small_groups_and_hides_the_interpretation(self):
        resp = self.open(BY_NAME["breakdown"])
        self.assertTemplateUsed(resp, "hr/breakdown.html")
        self.assertContains(resp, "(60% × 3.93) + (40% × 4.10) = 4.00")  # 4 peers: merged with students
        self.assertNotContains(resp, '<th scope="row" class="ds-cell-strong">Peers</th>')
        evaluations = self.open(BY_NAME["evaluations"]).context["results"]
        dana = next(r for r in evaluations if r["name"] == "Dana Villanueva")
        self.assertEqual(dana["overall"], resp.context["computation"]["overall"])
        self.assertNotContains(resp, "Copy interpretation")  # the AI interpretation is the employee's alone

    def test_wellness_shows_groups_only(self):
        resp = self.open(BY_NAME["wellness"])
        self.assertTemplateUsed(resp, "hr/wellness.html")
        burnout = {b["name"]: (b["score"], b["level"]) for b in resp.context["burnout"]}
        self.assertEqual(burnout["College of Engineering"], (72, "High"))  # the dashboard's alerts
        self.assertEqual(burnout["Basic Education"], (58, "Watch"))
        headcount = {d["name"]: d["headcount"] for d in DEPTS}
        self.assertTrue(all(headcount[name] >= 5 for name in burnout))  # plan §7.3, rule 1
        self.assertContains(resp, "groups of 5 or more people only")

    def test_messages_and_assistant_follow_the_dashboard(self):
        messages = self.open(BY_NAME["messages"])
        self.assertTemplateUsed(messages, "hr/messages.html")
        self.assertContains(messages, "Is there anything else HR needs from me?")
        for concern in messages.context["concerns"]:
            self.assertNotIn("name", concern)  # anonymous concerns carry no sender identity
        assistant = self.open(BY_NAME["assistant"])
        self.assertTemplateUsed(assistant, "hr/assistant.html")
        self.assertContains(assistant, "My payslip is missing the overload pay")
        self.assertContains(assistant, "<span data-handoff-count>3</span> open")

    def test_old_screens_are_gone(self):
        for path in ("/dashboard/", "/admin-dashboard/"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)

    def test_attendance_schedules_and_hours(self):
        resp = self.open(BY_NAME["attendance"])
        self.assertContains(resp, 'id="panel-schedules"')
        self.assertContains(resp, 'id="panel-hours"')
        schedules = resp.context["schedules"]
        self.assertEqual([s["total"] for s in schedules], [d["headcount"] for d in DEPTS])
        self.assertContains(resp, "data-say=", count=len(resp.context["schedule_issues"]))
        hours = resp.context["hours"]
        for row in hours:
            with self.subTest(department=row["name"]):
                self.assertEqual(row["logged"], row["expected"] + row["over"] - row["under"])
        # The department with the most overtime is the one whose burnout "hours above expected" factor is highest.
        burnout = {b["name"]: b["factors"][3]["score"] for b in WELLNESS["burnout"]}
        self.assertEqual(max(hours, key=lambda r: r["share"])["name"], max(burnout, key=burnout.get))

    def test_tracker_matches_the_career_lists(self):
        career = self.open(BY_NAME["career"])
        self.assertContains(career, "Goals this semester")
        self.assertEqual(career.context["goals_set"]["value"], sum(g["value"] for g in career.context["goals"]))
        self.assertContains(career, 'href="/career/tracker/#rowan-sison"')
        tracker = self.open(BY_NAME["tracker"])
        self.assertTemplateUsed(tracker, "hr/tracker.html")
        people = {p["name"]: p for p in tracker.context["people"]}
        for item in STAGNANT:
            if item["name"] in people:
                with self.subTest(stagnant=item["name"]):
                    p = people[item["name"]]
                    self.assertEqual((p["met"]["value"], p["met"]["total"]), (item["value"], item["total"]))
                    self.assertIn("Stagnant", p["flags"])
        ready = {r["name"] for r in PROMOTION_READY}
        for p in people.values():
            with self.subTest(person=p["name"]):
                self.assertEqual(p["met"]["value"] == p["met"]["total"], p["name"] in ready)
                self.assertEqual(sum(s["state"] == "current" for s in p["ladder"]), 1)
        self.assertContains(tracker, "data-tracker-person=", count=len(people))

    def test_messages_include_groups_and_the_hr_office(self):
        resp = self.open(BY_NAME["messages"])
        self.assertEqual({t["kind"] for t in THREADS}, {"employee", "group", "office"})
        self.assertTrue(all(t["messages"] for t in THREADS))
        self.assertContains(resp, "data-thread-pane=", count=len(THREADS))
        self.assertContains(resp, 'data-dialog-open="concern-dialog"', count=len(resp.context["concerns"]))

    def test_assistant_matching_explains_every_handoff(self):
        # The tester uses the assistant's rule: 2 matching words answer, fewer hands off (ties: earlier FAQ).
        def match(question):
            asked = set(re.findall(r"[a-z0-9]+", question.lower()))
            best = max(FAQ_ANSWERS, key=lambda f: len(asked & set(f["keywords"])))
            return best["title"], len(asked & set(best["keywords"]))

        for h in HANDOFFS:
            with self.subTest(question=h["question"]):
                title, hits = match(h["question"])
                self.assertLess(hits, 2)
                self.assertEqual(title if hits else "None", h["closest"])
        resp = self.open(BY_NAME["assistant"])
        for chip in resp.context["chips"][:3]:
            with self.subTest(chip=chip):
                self.assertGreaterEqual(match(chip)[1], 2)

    def test_wellness_checkins_add_up(self):
        resp = self.open(BY_NAME["wellness"])
        checkins = resp.context["checkins"]
        self.assertEqual(sum(c["value"] for c in checkins), 176)  # the "Checked in this week" tile
        mood = sum(c["mood"] * c["total"] for c in checkins) / SCHOOL["headcount"]
        self.assertAlmostEqual(mood, 3.6, delta=0.05)  # the "Average mood" tile
        self.assertEqual([c["stress"] for c in checkins], [DEPT_STRESS[d["name"]][-1] for d in DEPTS])
        self.assertContains(resp, 'href="/wellness/surveys/"')

    def test_survey_results_match_the_wellness_card(self):
        resp = self.open(BY_NAME["surveys"])
        self.assertTemplateUsed(resp, "hr/surveys.html")
        self.assertEqual(resp.context["index"], WELLNESS["survey"]["index"])
        for q in resp.context["questions"]:
            with self.subTest(question=q["statement"]):
                self.assertEqual(q["total"], SURVEY_RESPONSES)
        self.assertEqual(sum(d["value"] for d in resp.context["by_dept"]), SURVEY_RESPONSES)
        self.assertTrue(all(t["value"] >= resp.context["small_group"] for t in resp.context["themes"]))

    def test_every_icon_is_defined(self):
        # bundle.css names only the glyphs the screens use (the font holds them all). An undefined
        # name renders as an empty square, so check every page and every script that writes icons.
        static = Path(__file__).parent / "static" / "hr"
        css = (static / "portal" / "bundle.css").read_text() + (static / "css" / "app.css").read_text()
        defined = set(re.findall(r"\.ti-([a-z0-9-]+):before", css))
        used = {}
        for page in PAGES:
            for name in re.findall(r'class="ti ti-([a-z0-9-]+)[" ]', self.open(page).content.decode()):
                used.setdefault(name, page.name)
        for script in (static / "js").glob("*.js"):
            for name in re.findall(r"ti ti-([a-z0-9-]+)(?![a-z0-9-]*\$)", script.read_text()):
                used.setdefault(name, script.name)
        missing = {name: where for name, where in used.items() if name not in defined}
        self.assertEqual(missing, {})

    def test_no_button_is_inert(self):
        # Every button does something in the prototype: a data-* hook, a form submit, a tab or a disclosure.
        # Segmented options are handled by shell.js. The UI kit's demos are exempt.
        for page in PAGES:
            if page.name == "ui_kit":
                continue
            html = self.open(page).content.decode()
            for button in re.findall(r"<button\b[^>]*>", html):
                with self.subTest(page=page.name, button=button[:80]):
                    self.assertRegex(button, r'data-|type="submit"|role="tab"|aria-controls|class="ds-seg"')

    # ── Roles (plan §7.4, §9.1) ──

    def test_each_role_sees_only_its_own_pages(self):
        for key in ROLES:
            with self.subTest(role=key):
                resp = self.open(BY_NAME[ROLES[key].landing], role=key)
                self.assertEqual(resp.status_code, 200)
                shown = {p.name for group in resp.context["nav"] for p in group["pages"]}
                self.assertTrue(shown)
                self.assertTrue(all(key in BY_NAME[name].roles for name in shown))
        hr_nav = {p.name for g in self.open(BY_NAME["dashboard"]).context["nav"] for p in g["pages"]}
        self.assertNotIn("wellness_office", hr_nav)  # consented cases are the wellness officer's alone (§7.3, rule 2)
        self.assertNotIn("settings", hr_nav)

    def test_a_role_cannot_open_another_roles_page(self):
        resp = self.open(BY_NAME["records"], role="employee")
        self.assertEqual(resp.status_code, 403)
        self.assertContains(resp, "Not available as Employee", status_code=403)
        self.assertEqual(self.open(BY_NAME["me_records"], role="hr").status_code, 403)
        self.client.cookies[ROLE_COOKIE] = "employee"
        self.assertRedirects(self.client.get("/"), "/me/")  # each role lands on its own dashboard

    def test_view_as_remembers_the_role(self):
        resp = self.client.get("/view-as/?role=head")
        self.assertRedirects(resp, "/department/")
        self.assertEqual(self.client.cookies[ROLE_COOKIE].value, "head")
        self.assertContains(self.client.get("/department/"), '<option value="head" selected>')

    def test_department_head_decides_step_one_for_their_department(self):
        head = self.open(BY_NAME["approvals"], role="head")
        rows = head.context["rows"]
        self.assertTrue(rows)
        self.assertEqual({r["department"] for r in rows}, {"College of Engineering"})  # scope: Dept only
        self.assertContains(head, "data-leave-approve", count=len(rows))  # usability task 10
        self.assertContains(head, 'id="approve-dialog"')
        hr = self.open(BY_NAME["approvals"])
        self.assertNotContains(hr, "data-leave-approve")  # HR watches and reminds at step 1

    # ── Employee screens (usability tasks 1–9) ──

    def test_employee_dashboard_starts_before_time_in(self):
        resp = self.open(BY_NAME["me"], role="employee")
        self.assertContains(resp, "You haven't timed in yet")  # task 1: the afternoon shift starts at 12:00 PM
        self.assertContains(resp, 'data-dialog-open="qr-dialog"')
        self.assertContains(resp, '<div class="ds-user-name">Robin Cruz</div>')

    def test_employee_leave_and_time_record_match_hr(self):
        resp = self.open(BY_NAME["me_attendance"], role="employee")
        data = resp.context["leave_data"]
        self.assertEqual(data["balances"]["VL"]["left"], 12)  # task 2 starts from 12 vacation days
        self.assertIn("2026-11-01", data["no_work"])  # holidays are not counted
        late = [d["date"] for d in resp.context["dtr"] if d["status"].startswith("Late")]
        self.assertEqual(late, ["Thu, Oct 1", "Mon, Oct 5", "Fri, Oct 9"])  # HR's watch list
        self.assertContains(self.open(BY_NAME["attendance"]), "3 late arrivals: Oct 1, 5 and 9")
        self.assertEqual(resp.context["history"][0]["status"], "With HR")  # the sick leave in HR's queue

    def test_employee_payslip_shows_government_contributions(self):
        resp = self.open(BY_NAME["me_records"], role="employee")
        latest = resp.context["payslip"]
        labels = [d["label"] for d in latest["deductions"]]
        for agency in ("SSS", "PhilHealth", "Pag-IBIG"):
            self.assertIn(f"{agency} contribution", labels)  # task 3
        self.assertEqual(latest["net"], "₱14,287.50")  # ₱16,000.00 gross less ₱1,712.50
        self.assertContains(resp, "Correction pending")  # the address correction HR is reviewing

    def test_employee_career_and_breakdown_match_hr(self):
        career = self.open(BY_NAME["me_career"], role="employee")
        left = [r for r in career.context["p"]["requirements"] if r["state"] != "met"]
        self.assertEqual([r["label"] for r in left], ["Training hours"])  # task 4: one requirement left
        breakdown = self.open(BY_NAME["me_breakdown"], role="employee")
        overall = breakdown.context["computation"]["overall"]
        robin = next(r for r in self.open(BY_NAME["evaluations"]).context["results"] if r["name"] == "Robin Cruz")
        self.assertEqual(overall, robin["overall"])  # task 8: the same rating HR shows
        self.assertContains(breakdown, "AI-generated interpretation. Your official rating is the computation above.")
        self.assertContains(breakdown, "data-ai-copy")  # task 9
        self.assertContains(breakdown, "data-ai-pdf")

    def test_ai_interpretation_quotes_only_breakdown_numbers(self):
        # Plan §5.5 guardrail: every number it quotes must come from the breakdown (or the previous rating).
        ctx = self.open(BY_NAME["me_breakdown"], role="employee").context
        comp = ctx["computation"]
        allowed = {comp["overall"], ctx["previous"], "5"} | {g["average_text"] for g in comp["groups"]}
        allowed |= {c["score"] for c in ctx["criteria"]}
        allowed.add(f"{float(comp['overall']) - float(ctx['previous']):.2f}")
        text = " ".join(t for _, t in ctx["interpretation"]["parts"]).replace(ctx["cycle"], "")
        quoted = set(re.findall(r"\d+(?:\.\d+)?", text))
        self.assertTrue(quoted)
        self.assertLessEqual(quoted, allowed)

    def test_employee_wellness_is_private(self):
        resp = self.open(BY_NAME["me_wellness"], role="employee")
        self.assertContains(resp, "Your check-ins are yours")
        self.assertEqual(resp.context["high_stress"], 3)  # the insight's "3 of your last 7"
        self.assertContains(resp, "data-concern-form")  # task 6
        self.assertContains(resp, 'name="mood"', count=5)  # task 5

    def test_links_stay_within_the_role(self):
        # A link to a screen the viewer's role cannot open would end on the no-access notice.
        by_path = {page.url: page for page in PAGES}
        for page in PAGES:
            for key in page.roles:
                html = self.open(page, role=key).content.decode()
                nav = html.split('aria-label="Main navigation"')[1].split("</nav>")[1]  # skip the sidebar itself
                for href in set(re.findall(r'href="(/[^"#?]*)', nav)):
                    if href.startswith("/static/") or href == "/view-as/":
                        continue
                    with self.subTest(page=page.name, role=key, href=href):
                        self.assertIn(href, by_path)
                        self.assertIn(key, by_path[href].roles)

    def test_view_as_returns_to_an_allowed_page_only(self):
        self.assertRedirects(self.client.get("/view-as/?role=hr&next=/records/"), "/records/")
        self.assertRedirects(self.client.get("/view-as/?role=employee&next=/records/"), "/me/")  # not theirs
        self.assertRedirects(self.client.get("/view-as/?role=hr&next=https://example.com/"), "/")  # no open redirect
        denied = self.open(BY_NAME["settings"], role="hr")
        self.assertContains(denied, "?role=admin&amp;next=/settings/", status_code=403)

    def test_static_files_are_versioned(self):
        # {% asset %} adds ?v=<last modified>, so a browser never keeps a stale bundle.css (and loses icons).
        for page in PAGES:
            html = self.open(page).content.decode()
            with self.subTest(page=page.name):
                links = re.findall(r'(?:href|src)="(/static/[^"]+)"', html)
                self.assertTrue(links)
                self.assertTrue(all(re.search(r"\?v=\d+$", link) for link in links), links)
