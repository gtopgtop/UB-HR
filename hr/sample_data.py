"""Sample data for the prototype screens, passed to templates as context (plan §9.1).

Everything here is invented and generic: no real school, person or department.
PageView merges `for_page(name)` into the context, so pages still make zero database queries.
"""

import calendar
from datetime import date, timedelta
from decimal import Decimal

from .charts import meter, sparkline


def peso(amount):
    return f"₱{amount:,.2f}"


CURRENT_USER = {"name": "Alex Rivera", "first_name": "Alex", "initials": "AR", "role": "HR Officer"}

SCHOOL_RATING_HISTORY = [("AY 2024–25 S1", 4.0), ("AY 2024–25 S2", 4.0), ("AY 2025–26 S1", 4.1),
                         ("AY 2025–26 S2", 4.2)]

# ── Today ───────────────────────────────────────────────────────────────────
# "Today" is Monday, October 12, 2026, at 11:20 AM.

YEAR, MONTH, TODAY, NOW = 2026, 10, 12, "11:20 AM"

APPROVAL_STATES = {"done": ("check", "approved"), "pending": ("hourglass", "waiting for a decision"),
                   "declined": ("x", "declined"), "waiting": ("clock", "not reached yet"),
                   "skipped": ("minus", "not needed")}


def _steps(*steps):
    return [{"label": label, "state": state, "icon": APPROVAL_STATES[state][0], "state_label": APPROVAL_STATES[state][1]}
            for label, state in steps]


# ── School calendar ─────────────────────────────────────────────────────────
# Layout and event types follow the Academic Calendar handoff, for design consistency.
# S.Y. 2026–2027 runs July 1 to June 30. Holidays are no-work days. "No Classes" days and
# breaks stop classes only, so staff still time in on them (plan §3, Module 2).

SCHOOL_YEAR = "2026-2027"
SCHOOL_NAME = "Faculty Management"

# value, label, colour, Tabler icon. The colours are the handoff's defaults.
CALENDAR_TYPES = [
    ("holiday", "Holiday", "#c92a2a", "flag"),
    ("exam", "Exam", "#1455a0", "writing"),
    ("enrollment", "Enrollment", "#2e6b0d", "clipboard-list"),
    ("quarter_break", "Break", "#7c3aed", "calendar-pause"),
    ("school_day_off", "No Classes", "#854f0b", "school-off"),
    ("event", "Event", "#a3266b", "star"),
    ("evaluation_period", "Evaluation Period", "#0b6e63", "report-analytics"),
    ("other", "Other", "#855c5c", "calendar"),
    ("personal", "My Event", "#3949ab", "user"),
]
NO_WORK_TYPES = {"holiday"}

# title, type, start, end (None = one day), description
SCHOOL_EVENTS = [
    ("Enrollment, 1st semester", "enrollment", "2026-07-06", "2026-07-24", "Faculty assist at the advising tables."),
    ("Faculty orientation and planning", "event", "2026-07-27", "2026-07-31", "Syllabus review and load assignment."),
    ("Classes begin, 1st semester", "event", "2026-08-03", None, None),
    ("Ninoy Aquino Day", "holiday", "2026-08-21", None, None),
    ("National Heroes Day", "holiday", "2026-08-31", None, None),
    ("Preliminary exams", "exam", "2026-09-14", "2026-09-18", None),
    ("Faculty general assembly", "event", "2026-10-09", None, "3:00 PM, AVR. Attendance is required."),
    ("Faculty wellness seminar", "event", "2026-10-15", None, "2:00 PM, AVR."),
    ("Midterm exams", "exam", "2026-10-19", "2026-10-23", None),
    ("1st semester evaluation period", "evaluation_period", "2026-10-26", "2026-11-14",
     "Student, peer and supervisor evaluations. The last day is when evaluations are due."),
    ("Foundation Day", "school_day_off", "2026-10-30", None, "No classes. Staff attend the foundation program."),
    ("All Saints' Day", "holiday", "2026-11-01", None, None),
    ("All Souls' Day (Special)", "holiday", "2026-11-02", None, None),
    ("Bonifacio Day", "holiday", "2026-11-30", None, None),
    ("Feast of the Immaculate Conception (Special)", "holiday", "2026-12-08", None, None),
    ("Final exams, 1st semester", "exam", "2026-12-14", "2026-12-18", None),
    ("Semestral break", "quarter_break", "2026-12-19", "2027-01-03", "No classes. Offices open on working days."),
    ("Christmas Eve (Special)", "holiday", "2026-12-24", None, None),
    ("Christmas Day", "holiday", "2026-12-25", None, None),
    ("Rizal Day", "holiday", "2026-12-30", None, None),
    ("New Year's Eve (Special)", "holiday", "2026-12-31", None, None),
    ("New Year's Day", "holiday", "2027-01-01", None, None),
    ("Enrollment, 2nd semester", "enrollment", "2027-01-04", "2027-01-08", None),
    ("Classes begin, 2nd semester", "event", "2027-01-11", None, None),
    ("Chinese New Year", "holiday", "2027-02-06", None, None),
    ("Preliminary exams, 2nd semester", "exam", "2027-02-15", "2027-02-19", None),
    ("People Power Anniversary (Special)", "holiday", "2027-02-25", None, None),
    ("Eid'l Fitr", "holiday", "2027-03-10", None, "Date subject to proclamation."),
    ("Midterm exams, 2nd semester", "exam", "2027-03-15", "2027-03-19", None),
    ("Maundy Thursday", "holiday", "2027-03-25", None, None),
    ("Good Friday", "holiday", "2027-03-26", None, None),
    ("Black Saturday (Special)", "holiday", "2027-03-27", None, None),
    ("Araw ng Kagitingan", "holiday", "2027-04-09", None, None),
    ("2nd semester evaluation period", "evaluation_period", "2027-04-19", "2027-05-08",
     "Student, peer and supervisor evaluations. The last day is when evaluations are due."),
    ("Labor Day", "holiday", "2027-05-01", None, None),
    ("Final exams, 2nd semester", "exam", "2027-05-10", "2027-05-14", None),
    ("Eid'l Adha", "holiday", "2027-05-17", None, "Date subject to proclamation."),
    ("Commencement exercises", "event", "2027-05-28", None, None),
    ("Summer break", "quarter_break", "2027-05-31", "2027-06-30", "No classes. Offices open on working days."),
    ("Faculty clearance and year-end reports", "other", "2027-06-01", "2027-06-11", None),
    ("Independence Day", "holiday", "2027-06-12", None, None),
]

PERSONAL_EVENTS = [
    ("HMO renewal meeting with the provider", "2026-10-14", None, "10:00 AM, HR conference room."),
    ("Payroll cutoff review", "2026-10-26", "2026-10-27", "Check overload and leave deductions before the Oct 31 run."),
    ("HR training: labor law updates", "2026-11-20", "2026-11-21", None),
    ("Submit the 201 file audit report", "2026-12-15", None, "For the HR director."),
]


def _event(i, title, kind, start, end, description):
    return {"event_id": i, "title": title, "event_type": kind, "start_date": start, "end_date": end or start,
            "description": description}


CALENDAR_EVENTS = [_event(i, *e) for i, e in enumerate(SCHOOL_EVENTS, start=1)]

# ── HR officer dashboard ────────────────────────────────────────────────────
# School-wide figures as of today at NOW. Every total is summed from DEPARTMENTS, so the tiles,
# the attendance panel and the evaluation cycle always agree.

# name, headcount, on leave today, timed in so far, of whom late, evaluators not yet assigned
DEPARTMENTS = [
    ("College of Computing", 36, 2, 31, 3, 0),
    ("College of Business", 39, 1, 35, 2, 0),
    ("College of Education", 32, 2, 28, 1, 0),
    ("College of Engineering", 37, 1, 32, 4, 9),
    ("College of Arts and Sciences", 47, 3, 40, 3, 0),
    ("Basic Education", 34, 2, 29, 2, 14),
    ("Administrative offices", 23, 1, 19, 2, 0),
]
ON_LEAVE_TODAY = [("Vacation leave", 8), ("Sick leave", 3), ("Emergency leave", 1)]
LEAVE_WAIT_LIMIT, COMPUTATION_WAIT_LIMIT = 3, 5  # working days, plan §5.4


def _department(name, headcount, on_leave, present, late, unassigned):
    expected = headcount - on_leave
    return {"name": name, "headcount": headcount, "on_leave": on_leave, "expected": expected, "present": present,
            "late": late, "unassigned": unassigned, **meter(present, expected)}


def _working_days(days):
    return f"{days} working day{'' if days == 1 else 's'}"


DEPTS = [_department(*d) for d in DEPARTMENTS]
SCHOOL = {key: sum(d[key] for d in DEPTS) for key in ("headcount", "on_leave", "expected", "present", "late",
                                                       "unassigned")}

# Approved by the department head, waiting for HR (step 2). name, department, leave, dates, days, waiting
LEAVE_QUEUE = [
    {"name": name, "department": dept, "type": kind, "dates": dates, "days": days, "waiting": _working_days(wait),
     "overdue": wait > LEAVE_WAIT_LIMIT}
    for name, dept, kind, dates, days, wait in [
        ("Jamie Santos", "College of Education", "Vacation leave", "Oct 19–20", 2, 5),
        ("Robin Cruz", "Basic Education", "Sick leave", "Oct 7–8", 2, 4),
        ("Casey Lim", "College of Engineering", "Vacation leave", "Nov 3–6", 4, 4),
        ("Drew Mendoza", "College of Arts and Sciences", "Emergency leave", "Oct 9", 1, 2),
        ("Jordan Aquino", "College of Business", "Sick leave", "Oct 9", 1, 2),
        ("Kai Bautista", "Administrative offices", "Vacation leave", "Oct 26–27", 2, 1),
        ("Avery Ramos", "College of Computing", "Vacation leave", "Nov 16–17", 2, 1),
        ("Riley Pascual", "College of Education", "Vacation leave", "Nov 9–10", 2, 1),
        ("Quinn Flores", "College of Engineering", "Sick leave", "Oct 8", 1, 1),
    ]
]

# name, department, kind, filed, working days open
COMPUTATION_REQUESTS = [
    {"name": name, "department": dept, "kind": kind, "filed": filed, "open": _working_days(days),
     "overdue": days > COMPUTATION_WAIT_LIMIT}
    for name, dept, kind, filed, days in [
        ("Dana Villanueva", "College of Engineering", "Breakdown", "Oct 2", 6),
        ("Lee Navarro", "College of Business", "Breakdown", "Oct 7", 3),
        ("Sam Torres", "College of Arts and Sciences", "Recheck", "Oct 8", 2),
        ("Pat Gomez", "Basic Education", "Breakdown", "Oct 9", 1),
    ]
]

# Each alert says why it was raised (plan §5). level: High, Watch or Policy.
ALERT_TONES = {"High": "error", "Watch": "warning", "Policy": "info"}
ALERTS = [
    {"title": title, "reason": reason, "level": level, "tone": ALERT_TONES[level]}
    for title, reason, level in [
        ("Burnout risk: College of Engineering", "Score 72 · stress up four weeks in a row", "High"),
        ("Retention risk: 1 employee, College of Business", "2 years past expected time in rank, rating falling",
         "High"),
        ("Burnout risk: Basic Education", "Score 58 · at this rate, crosses High in about 3 weeks", "Watch"),
        ("Career stagnation: 3 employees, College of Arts and Sciences",
         "Past expected time in rank, under 60% of requirements met", "Watch"),
        ("Computation request open 6 working days", "Dana Villanueva, College of Engineering", "Policy"),
    ]
]

_leave_overdue = sum(r["overdue"] for r in LEAVE_QUEUE)
_requests_overdue = sum(r["overdue"] for r in COMPUTATION_REQUESTS)
_alerts_high = sum(a["level"] == "High" for a in ALERTS)
_outstanding = [d for d in DEPTS if d["unassigned"]]

DASHBOARD = {
    "subtitle": f"Welcome back, {CURRENT_USER['first_name']} · Monday, October 12 · 1st semester, AY 2026–2027",
    "stats": [
        {"label": "Present today", "value": SCHOOL["present"], "hint": f"of {SCHOOL['expected']} expected · {SCHOOL['late']} late",
         "icon": "user-check", "tone": "t-success"},
        {"label": "On leave today", "value": SCHOOL["on_leave"],
         "hint": " · ".join(f"{n} {kind.split()[0].lower()}" for kind, n in ON_LEAVE_TODAY), "icon": "plane-departure",
         "tone": "t-info"},
        {"label": "Leave to process", "value": len(LEAVE_QUEUE),
         "hint": f"{_leave_overdue} waiting over {LEAVE_WAIT_LIMIT} working days", "icon": "file-check",
         "tone": "t-warning"},
        {"label": "Computation requests", "value": len(COMPUTATION_REQUESTS),
         "hint": f"{_requests_overdue} open over {COMPUTATION_WAIT_LIMIT} working days", "icon": "list-check", "tone": ""},
        {"label": "Open alerts", "value": len(ALERTS), "hint": f"{_alerts_high} high", "icon": "alert-triangle",
         "tone": "t-error"},
    ],
    "attendance_today": {
        "as_of": NOW,
        "school": SCHOOL,
        "not_in": SCHOOL["expected"] - SCHOOL["present"],
        "pct": meter(SCHOOL["present"], SCHOOL["expected"])["pct"],
        "departments": DEPTS,
    },
    "leave_queue": LEAVE_QUEUE[:5],
    "leave_queue_total": len(LEAVE_QUEUE),
    "cycle": {
        "name": "1st semester, AY 2026–2027",
        "steps": [
            {"title": "Schedule memo", "caption": "Sent Oct 10", "state": "done"},
            {"title": "Evaluator assignment", "caption": "Due Oct 23", "state": "current"},
            {"title": "Evaluation period", "caption": "Oct 26 – Nov 14", "state": "next"},
            {"title": "Computation and release", "caption": "From Nov 16", "state": "next"},
        ],
        "progress": meter(SCHOOL["headcount"] - SCHOOL["unassigned"], SCHOOL["headcount"]),
        "departments": [
            {"label": d["name"], "note": f"{d['unassigned']} of {d['headcount']} unassigned", "done": False}
            for d in _outstanding
        ] + [{"label": f"{len(DEPTS) - len(_outstanding)} other departments", "note": "Done", "done": True}],
    },
    "rating": {
        "value": "4.2",
        "out_of": "5",
        "delta": "+0.1",
        "delta_period": "vs last semester",
        "trend": sparkline(SCHOOL_RATING_HISTORY),
        "raters": [
            {"label": "Student evaluation", "score": "4.3", **meter(4.3, 5)},
            {"label": "Peer evaluation", "score": "4.1", **meter(4.1, 5)},
            {"label": "Supervisor rating", "score": "4.2", **meter(4.2, 5)},
        ],
    },
    "computation_requests": COMPUTATION_REQUESTS,
    "alerts": ALERTS,
    "on_leave": [{"type": kind, **meter(n, SCHOOL["on_leave"])} for kind, n in ON_LEAVE_TODAY],
    "announcements": [
        {"title": "Evaluation schedule for the 1st semester", "kind": "Memo", "date": "Oct 10",
         **meter(201, SCHOOL["headcount"])},
        {"title": "Updated leave filing guidelines", "kind": "Policy", "date": "Oct 8",
         **meter(176, SCHOOL["headcount"])},
        {"title": "Faculty wellness seminar, 2:00 PM", "kind": "Event", "date": "Oct 15",
         **meter(132, SCHOOL["headcount"])},
    ],
    "handoffs": [
        {"question": "Can I convert unused sick leave to cash?", "department": "College of Business", "when": "2 h ago"},
        {"question": "My payslip is missing the overload pay", "department": "College of Computing", "when": "Yesterday"},
        {"question": "How do I update my civil status?", "department": "Basic Education", "when": "Oct 9"},
    ],
}


# ── Attendance (HR officer) ─────────────────────────────────────────────────
# School-wide daily attendance from July 1 to today: the calendar's attendance layer (handoff §10,
# with departments in place of sections). Past days are made up but steady, from a fixed formula, with
# a Monday tardiness bump. Today comes from DEPTS, so it matches the dashboard to the person.


def _past_department_day(day, i, dept):
    o = day.toordinal()
    on_leave = (o * 3 + i * 5) % 4
    absent = (o * 5 + i * 7) % 3
    present = dept["headcount"] - on_leave - absent
    late = min(present, (o * 7 + i * 11) % 5 + (2 if day.weekday() == 0 else 0))
    return {"name": dept["name"], "staff": dept["headcount"], "present": present, "late": late, "absent": absent,
            "on_leave": on_leave, "not_timed_in": 0}


def _today_department(dept):
    return {"name": dept["name"], "staff": dept["headcount"], "present": dept["present"], "late": dept["late"],
            "absent": 0, "on_leave": dept["on_leave"], "not_timed_in": dept["expected"] - dept["present"]}


def _rate(part, whole):
    return f"{part / whole * 100:.1f}%" if whole else "—"


def _school_day(departments):
    totals = {key: sum(d[key] for d in departments) for key in ("staff", "present", "late", "absent", "on_leave",
                                                                 "not_timed_in")}
    for d in departments:
        d["complete"] = d["not_timed_in"] == 0
    return {**totals, "rate": _rate(totals["present"], totals["staff"] - totals["on_leave"]), "departments": departments}


def _attendance_days():
    """One school-wide record per working day up to today, keyed by date. Weekends and holidays have none."""
    no_work = {e["start_date"] for e in CALENDAR_EVENTS if e["event_type"] in NO_WORK_TYPES}
    today = date(YEAR, MONTH, TODAY)
    days = {}
    day = date(2026, 7, 1)
    while day < today:
        if day.weekday() < 5 and day.isoformat() not in no_work:
            days[day.isoformat()] = _school_day([_past_department_day(day, i, d) for i, d in enumerate(DEPTS)])
        day += timedelta(days=1)
    days[today.isoformat()] = _school_day([_today_department(d) for d in DEPTS])
    return days


ATTENDANCE_DAYS = _attendance_days()
_TODAY_KEY = date(YEAR, MONTH, TODAY).isoformat()


def _closed_days(prefix):
    """The month's days that are over: today still has people who have not timed in."""
    return [r for k, r in ATTENDANCE_DAYS.items() if k.startswith(prefix) and k < _TODAY_KEY]


def _month_tally(prefix):
    days = _closed_days(prefix)
    present = sum(r["present"] for r in days)
    expected = sum(r["staff"] - r["on_leave"] for r in days)
    return [
        {"label": "Attendance rate", "value": _rate(present, expected), "tone": "success"},
        {"label": "Late arrivals", "value": sum(r["late"] for r in days), "tone": "warning"},
        {"label": "Leave days", "value": sum(r["on_leave"] for r in days), "tone": "info"},
        {"label": "Absences", "value": sum(r["absent"] for r in days), "tone": "error"},
    ]


_OCTOBER = _closed_days(f"{YEAR}-{MONTH:02d}-")
_oct_present = sum(r["present"] for r in _OCTOBER)
_oct_expected = sum(r["staff"] - r["on_leave"] for r in _OCTOBER)
_oct_late = sum(r["late"] for r in _OCTOBER)
_oct_monday_late = sum(r["late"] for k, r in ATTENDANCE_DAYS.items()
                       if r in _OCTOBER and date.fromisoformat(k).weekday() == 0)


def _department_month(i):
    rows = [r["departments"][i] for r in _OCTOBER]
    present, expected = sum(r["present"] for r in rows), sum(r["staff"] - r["on_leave"] for r in rows)
    return {**meter(present, expected), "rate": _rate(present, expected)}


ATTENDANCE_DEPARTMENTS = [
    {**d, "not_timed_in": d["expected"] - d["present"], "month": _department_month(i)} for i, d in enumerate(DEPTS)
]

CALENDAR = {
    "school_year": SCHOOL_YEAR,
    "school_name": SCHOOL_NAME,
    "today": _TODAY_KEY,
    "types": [{"value": v, "label": label, "color": color, "icon": icon} for v, label, color, icon in CALENDAR_TYPES],
    "no_work_types": sorted(NO_WORK_TYPES),
    "can_edit_school": True,  # HR officers keep the school calendar (handoff §6, ACADEMIC_STAFF)
    "events": CALENDAR_EVENTS,
    "mine": [_event(i, title, "personal", start, end, description)
             for i, (title, start, end, description) in enumerate(PERSONAL_EVENTS, start=1)],
    "attendance": ATTENDANCE_DAYS,
}

# Leave entitlement per employee per school year, and days used so far.
LEAVE_USAGE = [("VL", "Vacation leave", 15, 412), ("SL", "Sick leave", 10, 286), ("EL", "Emergency leave", 3, 61)]

# Policy alerts from plan §5.4. tone: warning for tardiness, error for unexplained absence, info for a missing log.
WATCH_LIST = [
    {"name": "Robin Cruz", "department": "Basic Education", "rule": "Late 3 or more times this month",
     "detail": "4 late arrivals: Oct 1, 5, 7 and 12", "notified": "Employee", "tone": "warning"},
    {"name": "Casey Lim", "department": "College of Engineering", "rule": "Late 3 or more times this month",
     "detail": "3 late arrivals · second month in a row", "notified": "Employee and department head", "tone": "warning"},
    {"name": "Pat Gomez", "department": "Basic Education", "rule": "Late 3 or more times this month",
     "detail": "3 late arrivals: Oct 2, 5 and 9", "notified": "Employee", "tone": "warning"},
    {"name": "Sam Torres", "department": "College of Arts and Sciences", "rule": "Absent with no leave filed",
     "detail": "Oct 9 · no time logs", "notified": "Employee and department head", "tone": "error"},
    {"name": "Lee Navarro", "department": "College of Business", "rule": "Timed in with no time out",
     "detail": "Oct 9 · in at 7:52 AM", "notified": "Employee", "tone": "info"},
]

# Every leave request this month. Step 2 (HR) is where the HR officer acts; the queue comes from LEAVE_QUEUE.
LEAVE_REQUESTS = [
    {**r, "steps": _steps(("Department head", "done"), ("HR", "pending")), "status": "With HR", "tone": "warning",
     "note": f"Waiting {r['waiting']}", "actionable": True}
    for r in LEAVE_QUEUE
] + [
    {"name": name, "department": dept, "type": kind, "dates": dates, "days": days, "steps": _steps(*steps),
     "status": status, "tone": tone, "note": note, "actionable": False}
    for name, dept, kind, dates, days, steps, status, tone, note in [
        ("Morgan Diaz", "College of Computing", "Vacation leave", "Oct 29", 1,
         (("Department head", "pending"), ("HR", "waiting")), "With department head", "", "Filed Oct 9"),
        ("Taylor Ong", "College of Business", "Sick leave", "Oct 13", 1,
         (("Department head", "pending"), ("HR", "waiting")), "With department head", "", "Filed Oct 12"),
        ("Jamie Santos", "College of Education", "Sick leave", "Oct 2", 1,
         (("Department head", "done"), ("HR", "done")), "Approved", "success", "HR: Medical certificate received."),
        ("Drew Mendoza", "College of Arts and Sciences", "Vacation leave", "Oct 5–6", 2,
         (("Department head", "done"), ("HR", "done")), "Approved", "success", "Classes covered by a substitute."),
        ("Kai Bautista", "Administrative offices", "Emergency leave", "Oct 1", 1,
         (("Department head", "declined"), ("HR", "skipped")), "Declined", "error",
         "Department head: Enrollment audit that day. Please refile."),
    ]
]

TIME_STATIONS = [
    {"name": "Main Building lobby", "kind": "QR and web", "last": "11:18 AM", "online": True},
    {"name": "Engineering Building", "kind": "QR", "last": "11:02 AM", "online": True},
    {"name": "Basic Education gate", "kind": "QR", "last": "7:58 AM", "online": False},
    {"name": "Library", "kind": "QR", "last": "10:41 AM", "online": True},
]

_school_today = ATTENDANCE_DAYS[_TODAY_KEY]

ATTENDANCE = {
    "subtitle": "School-wide time records, calendar and leave · Monday, October 12",
    "calendar": CALENDAR,
    "calendar_events_count": len(CALENDAR_EVENTS),
    "calendar_mine_count": len(PERSONAL_EVENTS),
    "today": {
        "as_of": NOW,
        **_school_today,
        "expected": _school_today["staff"] - _school_today["on_leave"],
        "complete": sum(d["complete"] for d in _school_today["departments"]),
        "meters": [
            {"label": "On time", "tone": "success", **meter(_school_today["present"] - _school_today["late"],
                                                             _school_today["staff"] - _school_today["on_leave"])},
            {"label": "Late", "tone": "warning", **meter(_school_today["late"],
                                                         _school_today["staff"] - _school_today["on_leave"])},
            {"label": "Not timed in yet", "tone": "", **meter(_school_today["not_timed_in"],
                                                              _school_today["staff"] - _school_today["on_leave"])},
        ],
    },
    "month": [
        {"label": "Attendance rate", "shown": _rate(_oct_present, _oct_expected),
         "note": f"{_oct_present:,} of {_oct_expected:,} person-days · {len(_OCTOBER)} working days so far",
         **meter(_oct_present, _oct_expected)},
        {"label": "On-time rate", "shown": _rate(_oct_present - _oct_late, _oct_present),
         "note": f"{_oct_late} late arrivals · {_oct_monday_late} of them on Mondays",
         **meter(_oct_present - _oct_late, _oct_present)},
    ],
    "tally": _month_tally(f"{YEAR}-{MONTH:02d}-"),
    "leave_usage": [
        {"code": code, "type": kind, "pending": sum(r["days"] for r in LEAVE_QUEUE if r["type"] == kind),
         **meter(used, per_person * SCHOOL["headcount"])}
        for code, kind, per_person, used in LEAVE_USAGE
    ],
    "departments": ATTENDANCE_DEPARTMENTS,
    "school": SCHOOL,
    "watch_list": WATCH_LIST,
    "leave_requests": LEAVE_REQUESTS,
    "leave_with_hr": len(LEAVE_QUEUE),
    "stations": TIME_STATIONS,
    "months": [calendar.month_name[m] for m in (7, 8, 9, 10)],
}

def _payslip(period, released, earnings, deductions):
    """Totals are computed from the items, so the figures always add up."""
    gross = sum(amount for _, amount in earnings)
    withheld = sum(amount for _, amount in deductions)
    return {
        "period": period,
        "released": released,
        "earnings": [{"label": label, "amount": peso(amount)} for label, amount in earnings],
        "deductions": [{"label": label, "amount": peso(amount)} for label, amount in deductions],
        "gross": peso(gross),
        "withheld": peso(withheld),
        "net": peso(gross - withheld),
    }


# ── Employee records (HR officer) ───────────────────────────────────────────
# The people named here are the same ones on the dashboard queues. Headcounts come from DEPTS.

# name, employee no., position, department, status, since, 201-file documents missing
EMPLOYEES = [
    {"name": name, "initials": "".join(part[0] for part in name.split()), "employee_no": no, "position": position,
     "department": dept, "status": status, "since": since, "missing": missing}
    for name, no, position, dept, status, since, missing in [
        ("Jamie Santos", "EMP-0312", "Associate Professor", "College of Education", "Full-time", "Jun 2015", 0),
        ("Robin Cruz", "EMP-0455", "Teacher II", "Basic Education", "Full-time", "Jun 2020", 1),
        ("Casey Lim", "EMP-0588", "Instructor", "College of Engineering", "Probationary", "Aug 2026", 2),
        ("Drew Mendoza", "EMP-0291", "Professor", "College of Arts and Sciences", "Full-time", "Jun 2012", 0),
        ("Jordan Aquino", "EMP-0502", "Assistant Professor", "College of Business", "Full-time", "Aug 2021", 0),
        ("Kai Bautista", "EMP-0219", "Administrative Officer II", "Administrative offices", "Full-time", "Jan 2010", 0),
        ("Avery Ramos", "EMP-0596", "Instructor", "College of Computing", "Part-time", "Aug 2026", 1),
        ("Dana Villanueva", "EMP-0347", "Assistant Professor", "College of Engineering", "Full-time", "Jun 2016", 0),
    ]
]
STATUS_COUNTS = [("Full-time", 219), ("Part-time", 17), ("Probationary", 12)]  # adds up to SCHOOL["headcount"]
STATUS_TONE = {"Full-time": "success", "Part-time": "info", "Probationary": "warning"}
for _e in EMPLOYEES:
    _e["tone"] = STATUS_TONE[_e["status"]]

CORRECTION_TONES = {"Pending": "warning", "Approved": "success", "Declined": "error"}
CORRECTIONS = [
    {"name": name, "department": dept, "field": field, "old": old, "new": new, "proof": proof, "filed": filed,
     "status": status, "tone": CORRECTION_TONES[status], "remark": remark}
    for name, dept, field, old, new, proof, filed, status, remark in [
        ("Robin Cruz", "Basic Education", "Address", "8 Old Road, Sample City", "21 Sample Avenue, Sample City",
         "Barangay certificate", "Oct 5", "Pending", ""),
        ("Jordan Aquino", "College of Business", "Civil status", "Single", "Married", "Marriage certificate",
         "Oct 7", "Pending", ""),
        ("Avery Ramos", "College of Computing", "Phone", "0917 000 2211", "0918 000 7788", "", "Oct 8", "Pending", ""),
        ("Casey Lim", "College of Engineering", "Emergency contact", "Lee Lim, Parent", "Sam Lim, Sibling", "",
         "Oct 9", "Pending", ""),
        ("Drew Mendoza", "College of Arts and Sciences", "Government ID", "TIN ending 112", "TIN ending 118",
         "BIR form 1905", "Sep 28", "Approved", "Matches the BIR record."),
        ("Kai Bautista", "Administrative offices", "Name", "Kai Bautista", "Kai Bautista-Ramos", "", "Sep 21",
         "Declined", "Attach a PSA-issued marriage certificate and refile."),
    ]
]
_corrections_pending = [c for c in CORRECTIONS if c["status"] == "Pending"]

# The record open beside the directory. HR officers may reveal IDs; every reveal is logged (plan §7.3).
SELECTED_RECORD = {
    "employee": EMPLOYEES[0],
    "personal": [
        ("Full name", "Jamie R. Santos"), ("Birth date", "July 2, 1984"), ("Civil status", "Married"),
        ("Address", "5 Sample Lane, Barangay Dos, Sample City"), ("Phone", "0917 000 4512"),
        ("Email", "jamie.santos@example.edu"),
    ],
    "emergency": [("Name", "Morgan Santos"), ("Relationship", "Spouse"), ("Phone", "0918 000 6623")],
    "government_ids": [
        {"id": "gov-sss", "label": "SSS", "full": "34-0000000-1", "masked": "••-•••••••-1"},
        {"id": "gov-philhealth", "label": "PhilHealth", "full": "12-000000000-7", "masked": "••-•••••••••-7"},
        {"id": "gov-pagibig", "label": "Pag-IBIG", "full": "1210-0000-0042", "masked": "••••-••••-0042"},
        {"id": "gov-tin", "label": "TIN", "full": "000-000-000-000", "masked": "•••-•••-•••-000"},
    ],
}

# Salary step dates within 60 days (plan §5.3, "Step increment due").
STEP_INCREMENTS = [
    {"name": "Jamie Santos", "department": "College of Education", "grade": "SG 18 · Step 4 → Step 5", "due": "Nov 1"},
    {"name": "Kai Bautista", "department": "Administrative offices", "grade": "SG 11 · Step 6 → Step 7", "due": "Nov 15"},
    {"name": "Dana Villanueva", "department": "College of Engineering", "grade": "SG 15 · Step 3 → Step 4", "due": "Dec 1"},
]

MOVEMENTS = [
    {"name": "Avery Ramos", "kind": "New hire", "detail": "Instructor, part-time · College of Computing", "date": "Aug 3, 2026", "tone": "success"},
    {"name": "Casey Lim", "kind": "New hire", "detail": "Instructor, probationary · College of Engineering", "date": "Aug 3, 2026", "tone": "success"},
    {"name": "Jordan Aquino", "kind": "Promotion", "detail": "Instructor → Assistant Professor · College of Business", "date": "Jun 1, 2026", "tone": "brand"},
    {"name": "Lee Navarro", "kind": "Transfer", "detail": "College of Computing → College of Business", "date": "Jun 1, 2026", "tone": "accent"},
    {"name": "Morgan Tan", "kind": "Separation", "detail": "Teacher I, resigned · Basic Education", "date": "May 31, 2026", "tone": "error"},
]

# School-wide payroll runs. Each is built like a payslip, so gross, deductions and net add up.
_RUN_EARNINGS = [("Basic pay", Decimal("5084000.00")), ("Teaching overload", Decimal("412800.00")),
                 ("Rice allowance", Decimal("248000.00"))]
_RUN_DEDUCTIONS = [("SSS contributions", Decimal("124000.00")), ("PhilHealth contributions", Decimal("127100.00")),
                   ("Pag-IBIG contributions", Decimal("24800.00")), ("Withholding tax", Decimal("298640.40"))]
_RUN_NO_OVERLOAD = _RUN_EARNINGS[:1] + _RUN_EARNINGS[2:]
_RUN_LOWER_TAX = _RUN_DEDUCTIONS[:3] + [("Withholding tax", Decimal("271800.00"))]


def _run(period, status, tone, earnings, deductions):
    return {**_payslip(period, status, earnings, deductions), "tone": tone, "employees": SCHOOL["headcount"]}


PAYROLL_RUNS = [
    _run("Oct 1–15, 2026", "For release Oct 15", "warning", _RUN_EARNINGS, _RUN_DEDUCTIONS),
    _run("Sep 16–30, 2026", "Released Sep 30", "success", _RUN_EARNINGS, _RUN_DEDUCTIONS),
    _run("Sep 1–15, 2026", "Released Sep 15", "success", _RUN_NO_OVERLOAD, _RUN_LOWER_TAX),
    _run("Aug 16–31, 2026", "Released Aug 31", "success", _RUN_NO_OVERLOAD, _RUN_LOWER_TAX),
]

# Monthly remittances, employee and employer shares together. A PhilHealth rate change took effect in June.
_R_EARLY = (Decimal("708800.00"), Decimal("496000.00"), Decimal("99200.00"), Decimal("597280.80"))
_R_LATE = (Decimal("708800.00"), Decimal("533200.00"), Decimal("99200.00"), Decimal("640610.00"))
_R_MONTHS = [(month, _R_EARLY if i < 5 else _R_LATE, "Due Nov 10" if month == "October" else f"Remitted {month[:3]} 10")
             for i, month in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                        "September", "October"])]

REMITTANCES = {
    "columns": ["SSS", "PhilHealth", "Pag-IBIG", "Withholding tax"],
    "rows": [{"month": month, "amounts": [peso(a) for a in amounts], "total": peso(sum(amounts)), "status": status,
              "tone": "warning" if status.startswith("Due") else "success"} for month, amounts, status in _R_MONTHS],
    "totals": [peso(sum(amounts[i] for _, amounts, _ in _R_MONTHS)) for i in range(4)],
    "grand_total": peso(sum(sum(amounts) for _, amounts, _ in _R_MONTHS)),
}

BENEFITS = [
    {"name": "Health card (HMO)", "detail": "Employee and up to two dependents", "coverage": "Jan 1 – Dec 31, 2026",
     "icon": "heart", "eligible_note": "of all employees", **meter(231, SCHOOL["headcount"])},
    {"name": "Group life insurance", "detail": "Twice the annual basic pay", "coverage": "Automatic for every employee",
     "icon": "shield-check", "eligible_note": "of all employees", **meter(SCHOOL["headcount"], SCHOOL["headcount"])},
    {"name": "Dependents' tuition discount", "detail": "50% for up to two children", "coverage": "AY 2026–2027",
     "icon": "gift", "eligible_note": "of employees with children", **meter(64, 118)},
    {"name": "Retirement plan", "detail": "Employer matches 5% of basic pay", "coverage": "Regular employees",
     "icon": "cash", "eligible_note": "of regular employees", **meter(187, 205)},
]

FILE_TONES = {"Overdue": "error", "Requested": "warning"}
MISSING_DOCUMENTS = [
    {"name": name, "department": dept, "document": doc, "requested": requested, "status": status,
     "tone": FILE_TONES[status]}
    for name, dept, doc, requested, status in [
        ("Casey Lim", "College of Engineering", "NBI clearance", "Aug 3", "Overdue"),
        ("Casey Lim", "College of Engineering", "Transcript of records", "Aug 3", "Overdue"),
        ("Avery Ramos", "College of Computing", "Pre-employment medical certificate", "Aug 3", "Overdue"),
        ("Robin Cruz", "Basic Education", "Renewed PRC license", "Sep 14", "Requested"),
        ("Pat Gomez", "Basic Education", "Training certificate: Child protection", "Sep 21", "Requested"),
    ]
]
INCOMPLETE_FILES, DOCUMENTS_MISSING = 11, 14

UPLOADS_TO_VERIFY = [
    {"name": "Marriage certificate (PSA)", "employee": "Jordan Aquino", "category": "Civil status",
     "uploaded": "Oct 7, 2026", "size": "PDF · 0.8 MB"},
    {"name": "Training certificate: Research ethics", "employee": "Dana Villanueva", "category": "Certificate",
     "uploaded": "Oct 6, 2026", "size": "PDF · 0.5 MB"},
    {"name": "BIR form 1905", "employee": "Drew Mendoza", "category": "Government ID",
     "uploaded": "Sep 27, 2026", "size": "PDF · 0.3 MB"},
]

RECORDS = {
    "stats": [
        {"label": "Employees", "value": SCHOOL["headcount"],
         "hint": " · ".join(f"{n} {s.lower()}" for s, n in STATUS_COUNTS), "icon": "users", "tone": ""},
        {"label": "Corrections to review", "value": len(_corrections_pending),
         "hint": f"Oldest filed {_corrections_pending[0]['filed']}", "icon": "edit", "tone": "t-warning"},
        {"label": "Incomplete 201 files", "value": INCOMPLETE_FILES, "hint": f"{DOCUMENTS_MISSING} documents missing",
         "icon": "file-alert", "tone": "t-error"},
        {"label": "Next payroll release", "value": "Oct 15",
         "hint": f"{PAYROLL_RUNS[0]['period']} · {SCHOOL['headcount']} payslips", "icon": "receipt", "tone": "t-info"},
    ],
    "employees": EMPLOYEES,
    "record": SELECTED_RECORD,
    "corrections": CORRECTIONS,
    "corrections_pending": len(_corrections_pending),
    "status_counts": [{"label": s, **meter(n, SCHOOL["headcount"])} for s, n in STATUS_COUNTS],
    "departments": DEPTS,
    "step_increments": STEP_INCREMENTS,
    "movements": MOVEMENTS,
    "payroll": PAYROLL_RUNS[0],
    "payroll_runs": PAYROLL_RUNS,
    "remittances": REMITTANCES,
    "benefits": BENEFITS,
    "files_complete": meter(SCHOOL["headcount"] - INCOMPLETE_FILES, SCHOOL["headcount"]),
    "missing_documents": MISSING_DOCUMENTS,
    "documents_missing": DOCUMENTS_MISSING,
    "uploads": UPLOADS_TO_VERIFY,
}

# ── Wellness (HR officer) ───────────────────────────────────────────────────
# Aggregates only, for groups of 5 or more (plan §7.3, rule 1). Individual check-ins never reach HR.
# Burnout scores follow plan §5.1: each factor is scored 0–100 and weighted; the levels are
# 0–49 Normal, 50–69 Watch, 70+ High.

BURNOUT_FACTORS = [  # label, weight %, data source
    ("Average stress, 4-week trend", 30, "Mood check-ins"),
    ("Average mood, 4-week trend", 25, "Mood check-ins"),
    ("Check-ins with stress 4 or higher", 15, "Mood check-ins"),
    ("Hours above expected", 15, "Attendance"),
    ("Unused leave late in the term", 10, "Leave balances"),
    ("Drop in check-in participation", 5, "Mood check-ins"),
]
# Factor scores per department, in BURNOUT_FACTORS order.
BURNOUT_SCORES = {
    "College of Computing": (40, 35, 30, 45, 30, 20),
    "College of Business": (25, 30, 20, 25, 35, 10),
    "College of Education": (45, 40, 35, 40, 25, 30),
    "College of Engineering": (85, 70, 78, 64, 55, 40),
    "College of Arts and Sciences": (30, 25, 20, 30, 40, 15),
    "Basic Education": (66, 58, 60, 50, 45, 50),
    "Administrative offices": (35, 30, 25, 55, 20, 10),
}
BURNOUT_LEVELS = [(70, "High", "error"), (50, "Watch", "warning"), (0, "Normal", "success")]


def _burnout(name):
    scores = BURNOUT_SCORES[name]
    score = round(sum(w * s for (_, w, _), s in zip(BURNOUT_FACTORS, scores)) / 100)
    level, tone = next((label, tone) for floor, label, tone in BURNOUT_LEVELS if score >= floor)
    return {"name": name, "score": score, "level": level, "tone": tone, **meter(score, 100),
            "factors": [{"label": label, "weight": w, "source": src, "score": s, "points": round(w * s / 100, 1),
                         **meter(s, 100)}
                        for (label, w, src), s in zip(BURNOUT_FACTORS, scores)]}


BURNOUT = sorted((_burnout(d["name"]) for d in DEPTS), key=lambda b: -b["score"])
_CHECKINS_THIS_WEEK = 176
MOOD_WEEKS = [("Sep 7", 3.9), ("Sep 14", 3.7), ("Sep 21", 3.8), ("Sep 28", 3.7), ("Oct 5", 3.6), ("Oct 12", 3.6)]
STRESS_WEEKS = [("Sep 7", 2.6), ("Sep 14", 3.0), ("Sep 21", 2.8), ("Sep 28", 2.9), ("Oct 5", 3.1), ("Oct 12", 3.1)]

WELLNESS = {
    "subtitle": "School-wide trends, burnout risk and interventions · groups of 5 or more only",
    "stats": [
        {"label": "Checked in this week", "value": f"{meter(_CHECKINS_THIS_WEEK, SCHOOL['headcount'])['pct']}%",
         "hint": f"{_CHECKINS_THIS_WEEK} of {SCHOOL['headcount']} employees", "icon": "heart", "tone": ""},
        {"label": "Average mood", "value": "3.6 / 5", "hint": "Down 0.3 over 6 weeks", "icon": "mood-smile",
         "tone": "t-warning"},
        {"label": "Average stress", "value": "3.1 / 5", "hint": "Up 0.5 over 6 weeks, midterms next week",
         "icon": "heart-rate-monitor", "tone": "t-error"},
        {"label": "Departments to watch", "value": sum(b["level"] != "Normal" for b in BURNOUT),
         "hint": " · ".join(f"{sum(b['level'] == lvl for b in BURNOUT)} {lvl.lower()}" for lvl in ("High", "Watch")),
         "icon": "alert-triangle", "tone": "t-error"},
    ],
    "burnout": BURNOUT,
    "focus": BURNOUT[0],
    "trends": [
        {"label": "Average mood", "value": MOOD_WEEKS[-1][1], "delta": "−0.3", "tone": "warning",
         "trend": sparkline(MOOD_WEEKS)},
        {"label": "Average stress", "value": STRESS_WEEKS[-1][1], "delta": "+0.5", "tone": "error",
         "trend": sparkline(STRESS_WEEKS)},
    ],
    "interventions": [
        {"title": "Workload review with the dean", "group": "College of Engineering", "owner": CURRENT_USER["name"],
         "follow_up": "Follow-up Oct 20", "status": "In progress", "tone": "info"},
        {"title": "Stress-management session after midterms", "group": "Basic Education", "owner": "Wellness office",
         "follow_up": "Scheduled Oct 26", "status": "Planned", "tone": ""},
        {"title": "Exam-week load balancing", "group": "College of Education", "owner": CURRENT_USER["name"],
         "follow_up": "Closed Sep 25", "status": "Done", "tone": "success"},
    ],
    "survey": {"title": "1st semester pulse survey", "closes": "Closes Oct 16", "index": "3.8", "index_delta": "+0.1",
               **meter(162, SCHOOL["headcount"])},
    "concern_topics": [{"topic": topic, **meter(n, 21)} for topic, n in
                       [("Workload", 9), ("Pay and benefits", 5), ("Facilities", 4), ("Working relationships", 3)]],
}

# ── Messages (HR officer) ───────────────────────────────────────────────────
# Threads with HR, anonymous concerns on HR topics, announcements and notifications. Messages are
# private to their participants (plan §7.4), so HR sees only threads it is part of.

THREADS = [
    {"id": "t1", "name": "Jamie Santos", "initials": "JS", "department": "College of Education",
     "subject": "Vacation leave, Oct 19–20", "preview": "Is there anything else HR needs from me?", "when": "Oct 9",
     "unread": 1, "messages": [
         {"from": "Jamie Santos", "mine": False, "when": "Oct 5, 3:12 PM",
          "text": "Hi, I filed vacation leave for Oct 19–20. Our dean approved it today."},
         {"from": CURRENT_USER["name"], "mine": True, "when": "Oct 6, 9:04 AM",
          "text": "Thanks, Jamie. It's in the HR queue now. We'll check it against your balance."},
         {"from": "Jamie Santos", "mine": False, "when": "Oct 9, 4:40 PM",
          "text": "It still shows as pending. Is there anything else HR needs from me? I have a family trip booked."},
     ]},
    {"id": "t2", "name": "Avery Ramos", "initials": "AR", "department": "College of Computing",
     "subject": "Overload pay on the Sep 30 payslip", "preview": "I taught two overload units in September.",
     "when": "Yesterday", "unread": 2, "messages": []},
    {"id": "t3", "name": "Casey Lim", "initials": "CL", "department": "College of Engineering",
     "subject": "NBI clearance for my 201 file", "preview": "My appointment is on Oct 20, I'll upload it after.",
     "when": "Oct 8", "unread": 0, "messages": []},
    {"id": "t4", "name": "College of Engineering heads", "initials": "CE", "department": "Department group · 4 people",
     "subject": "Evaluator assignment", "preview": "We still need peers for 9 faculty. Can the deadline move?",
     "when": "Oct 7", "unread": 0, "messages": []},
    {"id": "t5", "name": "Robin Cruz", "initials": "RC", "department": "Basic Education",
     "subject": "Address correction", "preview": "I attached the barangay certificate.", "when": "Oct 5",
     "unread": 0, "messages": []},
]

CONCERNS = [
    {"code": "Claim code ending 4F2", "topic": "Workload", "received": "Oct 11",
     "excerpt": "Three of us are covering a colleague's classes on top of our full loads, with no overload pay.",
     "status": "New", "tone": "warning"},
    {"code": "Claim code ending 9KD", "topic": "Pay and benefits", "received": "Oct 8",
     "excerpt": "The HMO did not accept my card at the clinic in town. Who do I ask?",
     "status": "Replied", "tone": "success"},
    {"code": "Claim code ending 2PA", "topic": "Facilities", "received": "Oct 2",
     "excerpt": "The faculty room air conditioner has been broken since August.", "status": "Replied",
     "tone": "success"},
]

NOTIFICATIONS = [
    {"icon": "file-check", "title": f"{_leave_overdue} leave requests waiting over {LEAVE_WAIT_LIMIT} working days",
     "detail": "Step 2 · oldest: Jamie Santos, 5 working days", "when": "Today, 8:00 AM", "tone": "t-warning"},
    {"icon": "list-check", "title": "Computation request open 6 working days",
     "detail": "Dana Villanueva, College of Engineering", "when": "Today, 8:00 AM", "tone": "t-error"},
    {"icon": "qrcode", "title": "Basic Education gate station is offline", "detail": "Last scan 7:58 AM",
     "when": "Today, 8:30 AM", "tone": "t-error"},
    {"icon": "cash", "title": "October remittances due Nov 10", "detail": "SSS, PhilHealth, Pag-IBIG and withholding tax",
     "when": "Yesterday", "tone": "t-info"},
    {"icon": "trending-up", "title": "3 step increments due in the next 60 days", "detail": "First one Nov 1, Jamie Santos",
     "when": "Oct 9", "tone": ""},
]

MESSAGES = {
    "threads": THREADS,
    "thread": THREADS[0],
    "unread": sum(t["unread"] for t in THREADS),
    "concerns": CONCERNS,
    "concerns_new": sum(c["status"] == "New" for c in CONCERNS),
    "announcements": DASHBOARD["announcements"],
    "audiences": ["All employees"] + [d["name"] for d in DEPTS],
    "notifications": NOTIFICATIONS,
}

# ── HR assistant (HR officer) ───────────────────────────────────────────────
# The assistant answers from the FAQ and hands anything it cannot match to HR (plan §3, Module 4).

ASSISTANT_QUESTIONS, ASSISTANT_ANSWERED = 412, 368
HANDOFFS = [
    {"name": "Jordan Aquino", "department": "College of Business", "question": DASHBOARD["handoffs"][0]["question"],
     "when": DASHBOARD["handoffs"][0]["when"], "closest": "Leave credits carried over", "match": "Low match"},
    {"name": "Avery Ramos", "department": "College of Computing", "question": DASHBOARD["handoffs"][1]["question"],
     "when": DASHBOARD["handoffs"][1]["when"], "closest": "Reading your payslip", "match": "Low match"},
    {"name": "Pat Gomez", "department": "Basic Education", "question": DASHBOARD["handoffs"][2]["question"],
     "when": DASHBOARD["handoffs"][2]["when"], "closest": "None", "match": "No match"},
]

ASSISTANT = {
    "stats": [
        {"label": "Questions this month", "value": ASSISTANT_QUESTIONS, "hint": "From 171 employees",
         "icon": "message-chatbot", "tone": ""},
        {"label": "Answered by the assistant", "value": f"{meter(ASSISTANT_ANSWERED, ASSISTANT_QUESTIONS)['pct']}%",
         "hint": f"{ASSISTANT_ANSWERED} of {ASSISTANT_QUESTIONS}", "icon": "circle-check", "tone": "t-success"},
        {"label": "Handed off to HR", "value": ASSISTANT_QUESTIONS - ASSISTANT_ANSWERED,
         "hint": f"{len(HANDOFFS)} still open", "icon": "inbox", "tone": "t-warning"},
        {"label": "Marked not helpful", "value": 7, "hint": "2 answers flagged twice or more", "icon": "thumb-down",
         "tone": "t-error"},
    ],
    "handoffs": HANDOFFS,
    "top_questions": [{"question": q, "faq": faq, **meter(n, 64)} for q, faq, n in [
        ("How many vacation days do I have left?", "Checking your leave balance", 64),
        ("When is the next payslip released?", "Payroll calendar", 51),
        ("How do I file sick leave?", "Filing sick leave", 38),
        ("Where do I upload my training certificate?", "Adding documents to your 201 file", 27),
        ("When are evaluations due?", "Evaluation schedule", 22),
    ]],
    "flagged": [
        {"faq": "Leave credits carried over", "votes": "3 not helpful this month",
         "reason": "Doesn't say whether unused sick leave can be converted to cash."},
        {"faq": "Reading your payslip", "votes": "2 not helpful this month",
         "reason": "Overload pay isn't explained; it appears a cutoff late."},
    ],
    "preview": [
        {"mine": True, "text": "How many vacation days do I have left?"},
        {"mine": False, "text": "You have 9 of 15 vacation days left for S.Y. 2026–2027, with 2 days pending approval. "
                                "From the FAQ: Checking your leave balance."},
    ],
    "chips": ["Where is my payslip?", "How do I file sick leave?", "When are evaluations due?"],
}

BY_PAGE = {"dashboard": DASHBOARD, "records": RECORDS, "attendance": ATTENDANCE, "wellness": WELLNESS,
           "messages": MESSAGES, "assistant": ASSISTANT}


def for_page(name):
    return BY_PAGE.get(name, {})
