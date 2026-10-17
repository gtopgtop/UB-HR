"""Every screen in the prototype: its route, sidebar entry and what it will hold.

The URLs, the sidebar, the page header and the placeholder pages all read from this
module, so adding a screen is one entry here. `planned`, `tier` and `iteration` are
copied from docs/plan.md (§9.2 screens, §11 build order). Nothing here touches the database.
"""

from dataclasses import dataclass

from django.urls import reverse

ITERATIONS = {2: "Employee", 3: "Oversight", 4: "Analytics", 5: "Polish"}


@dataclass(frozen=True)
class Page:
    name: str  # URL name, used as hr:<name>
    path: str
    title: str
    icon: str  # Tabler icon name without the ti- prefix
    subtitle: str = ""
    nav_label: str = ""  # shorter sidebar label, when the title is too long
    role: str = ""
    tier: str = ""
    iteration: int | None = None
    planned: tuple[str, ...] = ()
    parent: str | None = None  # page above this one in the breadcrumb trail
    template: str = "placeholder"

    @property
    def url(self):
        return reverse(f"hr:{self.name}")

    @property
    def label(self):
        return self.nav_label or self.title

    @property
    def iteration_name(self):
        return ITERATIONS.get(self.iteration, "")


@dataclass(frozen=True)
class Section:
    label: str
    pages: tuple[Page, ...]
    collapsible: bool = False  # collapsible sections start closed unless they hold the current page


EMPLOYEE, DEPT_HEAD, HR_OFFICER = "Employee", "Department Head", "HR Officer"

SECTIONS = (
    Section("My work", (
        Page("dashboard", "", "Dashboard", "layout-dashboard",
             subtitle="Layout sample with placeholder figures", role=EMPLOYEE, tier="Tier 1", iteration=2,
             template="dashboard"),
        Page("records", "records/", "My records", "id-badge-2",
             subtitle="Profile, employment history, pay and 201 file", role=EMPLOYEE, tier="Tier 1", iteration=2,
             planned=("Profile", "Employment history", "Payslips, contributions and benefits", "201 file",
                      "Correction request")),
        Page("attendance", "attendance/", "Attendance", "calendar-time",
             subtitle="Time in, daily time record and leave", role=EMPLOYEE, tier="Tier 1", iteration=2,
             planned=("Time in (web and QR)", "DTR calendar", "Schedule", "File leave", "Leave history")),
        Page("wellness", "wellness/", "Wellness", "heart",
             subtitle="Daily check-in, trends and support", role=EMPLOYEE, tier="Tier 1", iteration=2,
             planned=("Daily check-in and trends", "Insights", "Consent sharing", "Concern follow-up")),
        Page("messages", "messages/", "Messages", "message-2",
             subtitle="Messages, notifications and announcements", role=EMPLOYEE, tier="Tier 2", iteration=5,
             planned=("Messages", "Notification centre", "Announcements")),
        Page("assistant", "assistant/", "HR assistant", "message-chatbot",
             subtitle="Answers to common HR questions", role=EMPLOYEE, tier="Tier 2", iteration=5,
             planned=("Full-page assistant", "Handoff to HR")),
    )),
    Section("Career", (
        Page("career", "career/", "Career progress", "trending-up", nav_label="Progress",
             subtitle="Track, requirements and salary grade path", role=EMPLOYEE, tier="Tier 1", iteration=2,
             planned=("Career tracker", "Requirements for the next rank", "Salary grade path", "Goals",
                      "Recognition")),
        Page("evaluations", "career/evaluations/", "Evaluations", "award",
             subtitle="Performance evaluations to read and acknowledge", role=EMPLOYEE, tier="Tier 1", iteration=2,
             parent="career",
             planned=("Evaluations with acknowledge", "Each evaluation links to its breakdown")),
        Page("breakdown", "career/evaluations/breakdown/", "Evaluation breakdown", "calculator",
             subtitle="How the latest rating was computed", role=EMPLOYEE, tier="Tier 1", iteration=2,
             parent="evaluations",
             planned=("Rating computation, or the request button if it has not been released",
                      "Recheck request", "AI interpretation panel with Copy and Download PDF")),
    ), collapsible=True),
    Section("Department", (
        Page("department", "department/", "Department dashboard", "building-community", nav_label="Overview",
             subtitle="Your department at a glance", role=DEPT_HEAD, tier="Tier 1", iteration=3,
             planned=("Present today", "Approvals", "Evaluation status", "Feedback overdue", "Retention watchlist",
                      "Department wellness aggregate")),
        Page("approvals", "department/approvals/", "Leave approvals", "clipboard-check",
             subtitle="Step 1 of the leave approval chain", role=DEPT_HEAD, tier="Tier 1", iteration=3,
             planned=("Pending leave requests (step 1)", "Approve or decline with a remark")),
        Page("team", "department/team/", "Team", "users",
             subtitle="Roster, evaluations and feedback", role=DEPT_HEAD, tier="Tier 2", iteration=5,
             planned=("Roster", "Supervisor evaluations", "Feedback notes", "Recognition")),
    )),
    Section("HR office", (
        Page("hr_dashboard", "hr/", "HR dashboard", "chart-bar",
             subtitle="School-wide attendance, performance and wellness", role=HR_OFFICER, tier="Tier 1", iteration=3,
             planned=("Charts with department and period filters", "Export",
                      "Burnout, retention and stagnation panels")),
        Page("computation_requests", "hr/computation-requests/", "Computation requests", "list-check",
             subtitle="Evaluation breakdowns waiting for release", role=HR_OFFICER, tier="Tier 1", iteration=3,
             planned=("Request queue", "Release breakdown", "Resolve recheck")),
        Page("alerts", "hr/alerts/", "Alerts and interventions", "alert-triangle", nav_label="Alerts",
             subtitle="Why each alert was raised and what was done", role=HR_OFFICER, tier="Tier 1", iteration=3,
             planned=("Burnout, retention and stagnation alerts", "Why each alert was raised",
                      "Start an intervention")),
        Page("directory", "hr/directory/", "Employee directory", "address-book", nav_label="Directory",
             subtitle="Every employee's record", role=HR_OFFICER, tier="Tier 2", iteration=5,
             planned=("Employee directory", "Record view and edit")),
        Page("leave_processing", "hr/leave/", "Leave processing", "file-check",
             subtitle="Step 2 of the leave approval chain", role=HR_OFFICER, tier="Tier 2", iteration=5,
             planned=("Leave processing (step 2)",)),
        Page("communications", "hr/communications/", "Announcements and inbox", "speakerphone",
             nav_label="Announcements", subtitle="Announcements, concerns and saved reports", role=HR_OFFICER,
             tier="Tier 2", iteration=5,
             planned=("Announcements composer", "Concern inbox", "Saved report templates")),
    )),
    Section("Analytics", (
        Page("executive", "executive/", "Executive analytics", "chart-pie", nav_label="Executive",
             subtitle="Read-only, aggregates only", role="Executive", tier="Tier 1", iteration=4,
             planned=("Headcount", "Turnover", "Attendance", "Performance", "Engagement index", "Burnout map",
                      "Promotion pipeline")),
        Page("wellness_office", "wellness-office/", "Wellness dashboard", "heart-rate-monitor",
             nav_label="Wellness office", subtitle="Grouped trends and consented cases", role="Wellness Officer",
             tier="Tier 1", iteration=4,
             planned=("Aggregates", "Heatmap", "Consented cases", "Counselor requests", "Concern inbox",
                      "Interventions")),
    )),
    Section("Admin", (
        Page("settings", "settings/", "Settings", "settings",
             subtitle="Roles, rules and configuration", role="HR Admin",
             tier="Tier 2 (roles and risk weights: Tier 1)", iteration=4,
             planned=("Roles and permissions matrix", "Leave types", "Policy rules", "Career tracks", "Risk weights",
                      "FAQ editor", "Audit log")),
        Page("ui_kit", "ui/", "UI kit", "components",
             subtitle="Every layout component, for building new screens", template="ui_kit"),
    ), collapsible=True),
)

# Reached from the sidebar footer, not from a nav section.
ACCOUNT = Page("account", "account/", "My settings", "adjustments-horizontal",
               subtitle="Your own preferences")

PAGES = tuple(page for section in SECTIONS for page in section.pages) + (ACCOUNT,)
BY_NAME = {page.name: page for page in PAGES}


def crumbs(page):
    """The pages above `page`, outermost first."""
    trail = []
    while page.parent:
        page = BY_NAME[page.parent]
        trail.insert(0, page)
    return trail
