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


HR_OFFICER = "HR Officer"

SECTIONS = (
    Section("My work", (
        Page("dashboard", "", "Dashboard", "layout-dashboard",
             subtitle="School-wide attendance, leave, evaluations and alerts", role=HR_OFFICER, tier="Tier 1",
             iteration=2, template="dashboard"),
        Page("records", "records/", "Employee records", "id-badge-2", nav_label="Records",
             subtitle="Directory, corrections, payroll, remittances, benefits and 201 files", role=HR_OFFICER,
             tier="Tier 1", iteration=2, template="records"),
        Page("attendance", "attendance/", "Attendance", "calendar-time",
             subtitle="School-wide time records, calendar and leave", role=HR_OFFICER, tier="Tier 1", iteration=2,
             template="attendance"),
        Page("wellness", "wellness/", "Wellness", "heart",
             subtitle="School-wide trends, burnout risk and interventions", role=HR_OFFICER, tier="Tier 1",
             iteration=2, template="wellness"),
        Page("messages", "messages/", "Messages", "message-2",
             subtitle="Employee inbox, anonymous concerns, announcements and notifications", role=HR_OFFICER,
             tier="Tier 2", iteration=5, template="messages"),
        Page("assistant", "assistant/", "HR assistant", "message-chatbot",
             subtitle="Handoffs, most-asked questions and answers to review", role=HR_OFFICER, tier="Tier 2",
             iteration=5, template="assistant"),
    )),
    Section("Career", (
        Page("career", "career/", "Career progress", "trending-up", nav_label="Progress",
             subtitle="Promotion pipeline, requirements to verify, salary grades and flags", role=HR_OFFICER,
             tier="Tier 1", iteration=2, template="career"),
        Page("evaluations", "career/evaluations/", "Evaluations", "award",
             subtitle="The current cycle, results by department and acknowledgements", role=HR_OFFICER,
             tier="Tier 1", iteration=2, parent="career", template="evaluations"),
        Page("breakdown", "career/evaluations/breakdown/", "Evaluation breakdown", "calculator",
             subtitle="Release computations and resolve rechecks", role=HR_OFFICER, tier="Tier 1", iteration=2,
             parent="evaluations", template="breakdown"),
    ), collapsible=True),
    Section("Department", (
        Page("department", "department/", "Department dashboard", "building-community", nav_label="Overview",
             subtitle="One department as HR sees it", role=HR_OFFICER, tier="Tier 1", iteration=3,
             template="department"),
        Page("approvals", "department/approvals/", "Leave approvals", "clipboard-check",
             subtitle="Step 1 of the leave approval chain, by department head", role=HR_OFFICER, tier="Tier 1",
             iteration=3, template="approvals"),
        Page("team", "department/team/", "Team", "users",
             subtitle="One department's roster, evaluators, feedback and recognition", role=HR_OFFICER,
             tier="Tier 2", iteration=5, template="team"),
    )),
    Section("HR office", (
        Page("hr_dashboard", "hr/", "HR dashboard", "chart-bar",
             subtitle="School-wide attendance, performance and wellness", role=HR_OFFICER, tier="Tier 1", iteration=3,
             template="hr_dashboard"),
        Page("computation_requests", "hr/computation-requests/", "Computation requests", "list-check",
             subtitle="Evaluation breakdowns waiting for release", role=HR_OFFICER, tier="Tier 1", iteration=3,
             template="computation_requests"),
        Page("alerts", "hr/alerts/", "Alerts and interventions", "alert-triangle", nav_label="Alerts",
             subtitle="Why each alert was raised and what was done", role=HR_OFFICER, tier="Tier 1", iteration=3,
             template="alerts"),
        Page("directory", "hr/directory/", "Employee directory", "address-book", nav_label="Directory",
             subtitle="Every employee's record", role=HR_OFFICER, tier="Tier 2", iteration=5, template="directory"),
        Page("leave_processing", "hr/leave/", "Leave processing", "file-check",
             subtitle="Step 2 of the leave approval chain", role=HR_OFFICER, tier="Tier 2", iteration=5,
             template="leave_processing"),
        Page("communications", "hr/communications/", "Announcements and inbox", "speakerphone",
             nav_label="Announcements", subtitle="Announcements, concerns and saved reports", role=HR_OFFICER,
             tier="Tier 2", iteration=5, template="communications"),
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
