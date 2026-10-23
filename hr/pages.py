"""Every screen in the prototype: its route, sidebar entry and what it will hold.

The URLs, the sidebar, the page header and the placeholder pages all read from this
module, so adding a screen is one entry here. `planned`, `tier` and `iteration` are
copied from docs/plan.md (§9.2 screens, §11 build order). Nothing here touches the database.

Each page lists the roles that may open it (plan §7.4). The sidebar shows the current role's pages only,
and the "View as" switcher (plan §9.1) changes the role; there is no login in the prototype.
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
    roles: tuple[str, ...] = ("hr",)  # keys of ROLES that may open the page

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


@dataclass(frozen=True)
class Role:
    key: str
    label: str
    landing: str  # page name the switcher opens


ROLES = {r.key: r for r in (
    Role("employee", "Employee", "me"),
    Role("head", "Department Head", "department"),
    Role("hr", "HR Officer", "dashboard"),
    Role("admin", "HR Admin", "settings"),
    Role("executive", "Executive", "executive"),
    Role("wellness", "Wellness Officer", "wellness_office"),
)}
DEFAULT_ROLE = "hr"
HR_OFFICER = "HR Officer"
EMPLOYEE = ("employee",)

SECTIONS = (
    # ── Employee: one person's own records (plan §9.2, Employee rows) ──
    Section("My work", (
        Page("me", "me/", "My dashboard", "layout-dashboard", nav_label="Dashboard",
             subtitle="Today, your leave, pay, career and check-in", role="Employee", tier="Tier 1", iteration=2,
             template="me_dashboard", roles=EMPLOYEE),
        Page("me_records", "me/records/", "My records", "id-badge-2", nav_label="Records",
             subtitle="Profile, employment history, payslips, contributions, benefits and 201 file", role="Employee",
             tier="Tier 1", iteration=2, template="me_records", roles=EMPLOYEE),
        Page("me_attendance", "me/attendance/", "My attendance", "calendar-time", nav_label="Attendance",
             subtitle="Time in, your time record, schedule and leave", role="Employee", tier="Tier 1", iteration=2,
             template="me_attendance", roles=EMPLOYEE),
        Page("me_wellness", "me/wellness/", "My wellness", "heart", nav_label="Wellness",
             subtitle="Daily check-in, your trend, support and anonymous concerns · private to you", role="Employee",
             tier="Tier 1", iteration=2, template="me_wellness", roles=EMPLOYEE),
        Page("me_messages", "me/messages/", "My messages", "message-2", nav_label="Messages",
             subtitle="Conversations with HR, announcements and notifications", role="Employee", tier="Tier 2",
             iteration=5, template="me_messages", roles=EMPLOYEE),
        Page("me_assistant", "me/assistant/", "HR assistant", "message-chatbot",
             subtitle="Ask about leave, pay, records or evaluations", role="Employee", tier="Tier 2", iteration=5,
             template="me_assistant", roles=EMPLOYEE),
    )),
    Section("Career", (
        Page("me_career", "me/career/", "My career", "trending-up", nav_label="Progress",
             subtitle="Your ladder, requirements, goals, evaluations and recognition", role="Employee",
             tier="Tier 1", iteration=2, template="me_career", roles=EMPLOYEE),
        Page("me_breakdown", "me/career/breakdown/", "Evaluation breakdown", "calculator",
             subtitle="How your latest rating was computed, and what it means", role="Employee", tier="Tier 1",
             iteration=2, parent="me_career", template="me_breakdown", roles=EMPLOYEE),
    ), collapsible=True),

    # ── HR officer ──
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
        Page("surveys", "wellness/surveys/", "Engagement surveys", "clipboard-text", nav_label="Surveys",
             subtitle="Build anonymous surveys and read the results, groups of 5 or more only", role=HR_OFFICER,
             tier="Tier 1", iteration=2, parent="wellness", template="surveys"),
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
        Page("tracker", "career/tracker/", "Career progress tracker", "stairs-up", nav_label="Tracker",
             subtitle="One employee's ladder, requirements, goals and feedback", role=HR_OFFICER, tier="Tier 1",
             iteration=2, parent="career", template="tracker"),
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
             template="department", roles=("hr", "head")),
        Page("approvals", "department/approvals/", "Leave approvals", "clipboard-check",
             subtitle="Step 1 of the leave approval chain, by department head", role=HR_OFFICER, tier="Tier 1",
             iteration=3, template="approvals", roles=("hr", "head")),
        Page("team", "department/team/", "Team", "users",
             subtitle="One department's roster, evaluators, feedback and recognition", role=HR_OFFICER,
             tier="Tier 2", iteration=5, template="team", roles=("hr", "head")),
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
             subtitle="School-wide aggregates, read-only", role="Executive", tier="Tier 1", iteration=4,
             template="executive", roles=("executive",)),
        Page("wellness_office", "wellness-office/", "Wellness dashboard", "heart-rate-monitor",
             nav_label="Wellness office", subtitle="Grouped trends and consented cases", role="Wellness Officer",
             tier="Tier 1", iteration=4, template="wellness_office", roles=("wellness",)),
    )),
    Section("Admin", (
        Page("settings", "settings/", "Settings", "settings",
             subtitle="Roles, rules and configuration", role="HR Admin",
             tier="Tier 2 (roles and risk weights: Tier 1)", iteration=4, template="settings", roles=("admin",)),
    )),
    Section("Prototype", (
        Page("ui_kit", "ui/", "UI kit", "components",
             subtitle="Every layout component, for building new screens", template="ui_kit"),
    ), collapsible=True),
)

# Reached from the sidebar footer, not from a nav section.
ACCOUNT = Page("account", "account/", "My settings", "adjustments-horizontal",
               subtitle="Your profile, notifications and preferences", template="account")

PAGES = tuple(page for section in SECTIONS for page in section.pages) + (ACCOUNT,)
BY_NAME = {page.name: page for page in PAGES}


def role_of(request):
    """The role picked with the "View as" switcher, kept in a cookie so pages still make no database queries."""
    key = request.COOKIES.get(ROLE_COOKIE, DEFAULT_ROLE)
    return ROLES.get(key, ROLES[DEFAULT_ROLE])


ROLE_COOKIE = "fms_role"


def nav_for(role, current):
    """The sidebar for `role`: its sections, each with only the pages that role may open."""
    groups = []
    for section in SECTIONS:
        pages = [p for p in section.pages if role.key in p.roles]
        if pages:
            groups.append({"section": section, "pages": pages,
                           "open": not section.collapsible or current in pages})
    return groups


def crumbs(page):
    """The pages above `page`, outermost first."""
    trail = []
    while page.parent:
        page = BY_NAME[page.parent]
        trail.insert(0, page)
    return trail
