"""Sample data for the prototype screens, passed to templates as context (plan §9.1).

Everything here is invented and generic: no real school, person or department.
PageView merges `for_page(name)` into the context, so pages still make zero database queries.
"""

import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal

from .charts import meter, sparkline


def peso(amount):
    return f"₱{amount:,.2f}"


CURRENT_USER = {"name": "Alex Rivera", "first_name": "Alex", "initials": "AR", "role": "Assistant Professor"}

SCHOOL_RATING_HISTORY = [("AY 2024–25 S1", 4.0), ("AY 2024–25 S2", 4.0), ("AY 2025–26 S1", 4.1),
                         ("AY 2025–26 S2", 4.2)]

# ── Attendance ──────────────────────────────────────────────────────────────
# "Today" is Monday, October 12, 2026, at 11:20 AM. Hours are computed from the logs, less a 1-hour lunch.

YEAR, MONTH, TODAY, NOW = 2026, 10, 12, "11:20 AM"
TIME_IN_TODAY = "7:48 AM"

# day: (kind, time in, time out, minutes late or leave label)
DTR_LOGS = {
    1: ("present", "7:52 AM", "5:03 PM", 0),
    2: ("leave", None, None, "Sick leave"),
    5: ("late", "8:07 AM", "5:10 PM", 7),
    6: ("present", "7:46 AM", "5:01 PM", 0),
    7: ("present", "7:50 AM", "4:58 PM", 0),
    8: ("late", "8:12 AM", "5:05 PM", 12),
    9: ("present", "7:55 AM", "5:00 PM", 0),
}
LAST_WEEK = range(5, 10)
STATUS_TONES = {"present": "success", "late": "warning", "leave": "info", "absent": "error", "rest": "muted",
                "today": "brand", "upcoming": ""}


def _hours(start, end, lunch=1):
    span = datetime.strptime(end, "%I:%M %p") - datetime.strptime(start, "%I:%M %p")
    return round(span.total_seconds() / 3600 - lunch, 1)


def _day(day, weekend):
    log = DTR_LOGS.get(day)
    if day == TODAY:
        return {"day": day, "status": "today", "label": "Today", "times": f"In {TIME_IN_TODAY}",
                "hours": _hours(TIME_IN_TODAY, NOW, lunch=0)}
    if log:
        kind, start, end, extra = log
        if kind == "leave":
            return {"day": day, "status": kind, "label": extra, "times": "", "hours": 0}
        label = f"Late {extra} min" if kind == "late" else "Present"
        return {"day": day, "status": kind, "label": label, "times": f"{start} – {end}", "hours": _hours(start, end),
                "minutes_late": extra}
    if weekend:
        return {"day": day, "status": "rest", "label": "Rest day", "times": "", "hours": 0}
    if day < TODAY:
        return {"day": day, "status": "absent", "label": "Absent", "times": "", "hours": 0}
    return {"day": day, "status": "upcoming", "label": "", "times": "", "hours": 0}


def _dtr():
    weeks = []
    for week in calendar.Calendar(firstweekday=0).monthdayscalendar(YEAR, MONTH):
        weeks.append([_day(d, weekend=i >= 5) if d else None for i, d in enumerate(week)])
    for cell in (c for w in weeks for c in w if c):
        cell["tone"] = STATUS_TONES[cell["status"]]
        cell["weekday"] = calendar.day_name[calendar.weekday(YEAR, MONTH, cell["day"])]
    days = [c for w in weeks for c in w if c]
    worked = [c for c in days if c["status"] in ("present", "late", "today")]
    late = [c for c in days if c["status"] == "late"]
    return {
        "title": f"{calendar.month_name[MONTH]} {YEAR}",
        "weekdays": [(name[:3], name) for name in calendar.day_name],
        "weeks": weeks,
        "log": [c for c in reversed(days) if c["status"] not in ("upcoming", "rest")],
        "summary": [
            {"label": "Days present", "value": len(worked), "tone": "success"},
            {"label": "Late", "value": f"{len(late)} · {sum(c['minutes_late'] for c in late)} min", "tone": "warning"},
            {"label": "On leave", "value": sum(c["status"] == "leave" for c in days), "tone": "info"},
            {"label": "Absent", "value": sum(c["status"] == "absent" for c in days), "tone": "error"},
        ],
        "hours_month": round(sum(c["hours"] for c in days), 1),
        "hours_last_week": round(sum(days[d - 1]["hours"] for d in LAST_WEEK), 1),
        "workdays": sum(1 for w in weeks for i, c in enumerate(w) if c and i < 5),
    }


DTR = _dtr()
EXPECTED_MONTH = DTR["workdays"] * 8

LEAVE_TYPES = [
    {"code": "VL", "type": "Vacation leave", "pending": 2, "attachment": False, **meter(9, 15)},
    {"code": "SL", "type": "Sick leave", "pending": 0, "attachment": True, **meter(6, 10)},
    {"code": "EL", "type": "Emergency leave", "pending": 0, "attachment": False, **meter(3, 3)},
]

WEEKLY_SCHEDULE = [
    ("Monday", [
        {"time": "9:00 – 10:30", "title": "IT 312 Database Systems", "place": "Room 204"},
        {"time": "1:00 – 2:30", "title": "IT 301 Systems Analysis and Design", "place": "Room 305"},
        {"time": "3:00 – 4:00", "title": "Department meeting", "place": "Faculty room"},
    ]),
    ("Tuesday", [
        {"time": "10:30 – 12:00", "title": "IT 205 Web Development", "place": "Lab 2"},
        {"time": "2:00 – 4:00", "title": "Consultation hours", "place": "Faculty room"},
    ]),
    ("Wednesday", [
        {"time": "9:00 – 10:30", "title": "IT 312 Database Systems", "place": "Room 204"},
        {"time": "1:00 – 2:30", "title": "IT 301 Systems Analysis and Design", "place": "Room 305"},
    ]),
    ("Thursday", [
        {"time": "10:30 – 12:00", "title": "IT 205 Web Development", "place": "Lab 2"},
        {"time": "2:00 – 5:00", "title": "Capstone advising", "place": "Lab 4"},
    ]),
    ("Friday", [
        {"time": "9:00 – 11:00", "title": "Research time", "place": "Library"},
        {"time": "1:00 – 2:30", "title": "IT 205 Web Development", "place": "Lab 2"},
    ]),
    ("Saturday", []),
]

APPROVAL_STATES = {"done": ("check", "approved"), "pending": ("hourglass", "waiting for a decision"),
                   "declined": ("x", "declined"), "waiting": ("clock", "not reached yet"),
                   "skipped": ("minus", "not needed")}


def _steps(*steps):
    return [{"label": label, "state": state, "icon": APPROVAL_STATES[state][0], "state_label": APPROVAL_STATES[state][1]}
            for label, state in steps]


LEAVE_HISTORY = [
    {"type": "Vacation leave", "dates": "Nov 3–4, 2026", "days": 2, "filed": "Oct 9", "status": "Pending",
     "tone": "warning", "steps": _steps(("Department head", "pending"), ("HR", "waiting")), "remarks": ""},
    {"type": "Sick leave", "dates": "Oct 2, 2026", "days": 1, "filed": "Oct 5", "status": "Approved",
     "tone": "success", "steps": _steps(("Department head", "done"), ("HR", "done")),
     "remarks": "HR: Medical certificate received."},
    {"type": "Vacation leave", "dates": "Aug 10–12, 2026", "days": 3, "filed": "Jul 27", "status": "Approved",
     "tone": "success", "steps": _steps(("Department head", "done"), ("HR", "done")),
     "remarks": "Department head: Classes covered by a substitute."},
    {"type": "Emergency leave", "dates": "Jun 22, 2026", "days": 1, "filed": "Jun 22", "status": "Declined",
     "tone": "error", "steps": _steps(("Department head", "declined"), ("HR", "skipped")),
     "remarks": "Department head: Overlaps the final exams. Please refile for another date."},
]

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
    ("Dentist appointment", "2026-10-14", None, "4:30 PM, after classes."),
    ("Capstone defense panel", "2026-10-27", "2026-10-28", "Panel member for two groups, Lab 4."),
    ("Faculty training: outcomes-based assessment", "2026-11-20", "2026-11-21", None),
    ("Submit journal article draft", "2026-12-15", None, "Goal for this semester."),
]

# Time logs before October, made up but steady: on time most days, three late days, one leave.
_LATE = {date(2026, 7, 14): ("8:05 AM", 5), date(2026, 8, 18): ("8:15 AM", 15), date(2026, 9, 8): ("8:03 AM", 3)}
_ON_LEAVE = {date(2026, 8, d): "Vacation leave" for d in (10, 11, 12)}


def _event(i, title, kind, start, end, description):
    return {"event_id": i, "title": title, "event_type": kind, "start_date": start, "end_date": end or start,
            "description": description}


def _record(status, label, time_in=None, time_out=None, minutes_late=0):
    hours = _hours(time_in, time_out) if time_in and time_out else 0
    return {"status": status, "label": label, "tone": STATUS_TONES[status], "time_in": time_in,
            "time_out": time_out, "hours": hours, "minutes_late": minutes_late}


def _attendance_days():
    """Your daily time record from July 1 to today, keyed by date: the calendar's attendance layer."""
    no_work = {e["start_date"] for e in CALENDAR_EVENTS if e["event_type"] in NO_WORK_TYPES}
    days = {}
    day = date(2026, 7, 1)
    while day < date(YEAR, MONTH, 1):
        key = day.isoformat()
        if day.weekday() < 5 and key not in no_work:
            if day in _ON_LEAVE:
                days[key] = _record("leave", _ON_LEAVE[day])
            elif day in _LATE:
                start, late = _LATE[day]
                days[key] = _record("late", f"Late {late} min", start, f"5:0{day.day % 10} PM", late)
            else:
                start = f"7:{40 + (day.day * 7 + day.month * 3) % 19:02d} AM"
                days[key] = _record("present", "On time", start, f"5:0{day.day % 10} PM")
        day += timedelta(days=1)
    for cell in (c for week in DTR["weeks"] for c in week if c):
        key = date(YEAR, MONTH, cell["day"]).isoformat()
        log = DTR_LOGS.get(cell["day"])
        if cell["status"] == "today":
            days[key] = {**_record("present", "On time", TIME_IN_TODAY), "hours": cell["hours"], "still_in": True}
        elif cell["status"] in ("present", "late"):
            days[key] = _record(cell["status"], "On time" if cell["status"] == "present" else cell["label"],
                                log[1], log[2], log[3])
        elif cell["status"] in ("leave", "absent"):
            days[key] = _record(cell["status"], cell["label"])
    return days


CALENDAR_EVENTS = [_event(i, *e) for i, e in enumerate(SCHOOL_EVENTS, start=1)]

CALENDAR = {
    "school_year": SCHOOL_YEAR,
    "school_name": SCHOOL_NAME,
    "today": date(YEAR, MONTH, TODAY).isoformat(),
    "types": [{"value": v, "label": label, "color": color, "icon": icon} for v, label, color, icon in CALENDAR_TYPES],
    "no_work_types": sorted(NO_WORK_TYPES),
    "events": CALENDAR_EVENTS,
    "mine": [_event(i, title, "personal", start, end, description)
             for i, (title, start, end, description) in enumerate(PERSONAL_EVENTS, start=1)],
    "attendance": _attendance_days(),
}

ATTENDANCE = {
    "subtitle": "Time in, daily time record, schedule and leave",
    "calendar": CALENDAR,
    "calendar_events_count": len(CALENDAR_EVENTS),
    "calendar_mine_count": len(PERSONAL_EVENTS),
    "clock": {"state": "in", "time_in": TIME_IN_TODAY, "status": "On time", "station": "Main Building lobby",
              "logs": [{"direction": "In", "time": TIME_IN_TODAY, "method": "Web"}]},
    "hours": [
        {"label": "This month", "note": f"{DTR['workdays']} working days", **meter(DTR["hours_month"], EXPECTED_MONTH)},
        {"label": "Last week", "note": f"Overtime {max(0, round(DTR['hours_last_week'] - 40, 1))} h",
         **meter(DTR["hours_last_week"], 40)},
    ],
    "leave_types": LEAVE_TYPES,
    "dtr": DTR,
    "schedule": WEEKLY_SCHEDULE,
    "leave_history": LEAVE_HISTORY,
}

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


_EARNINGS = [("Basic pay", Decimal("21500.00")), ("Teaching overload", Decimal("3200.00")),
             ("Rice allowance", Decimal("1000.00"))]
_DEDUCTIONS = [("SSS contribution", Decimal("500.00")), ("PhilHealth contribution", Decimal("537.50")),
               ("Pag-IBIG contribution", Decimal("100.00")), ("Withholding tax", Decimal("1412.40"))]

PAYSLIPS = [
    _payslip("Oct 1–15, 2026", "Oct 15", _EARNINGS, _DEDUCTIONS),
    _payslip("Sep 16–30, 2026", "Sep 30", _EARNINGS, _DEDUCTIONS),
    _payslip("Sep 1–15, 2026", "Sep 15", _EARNINGS[:1] + _EARNINGS[2:], _DEDUCTIONS[:3] + [("Withholding tax", Decimal("932.40"))]),
    _payslip("Aug 16–31, 2026", "Aug 31", _EARNINGS[:1] + _EARNINGS[2:], _DEDUCTIONS[:3] + [("Withholding tax", Decimal("932.40"))]),
]

# Monthly employee share: SSS, PhilHealth, Pag-IBIG, withholding tax. A rate change took effect in June.
_EARLY, _LATE = (Decimal("1000"), Decimal("1000"), Decimal("200"), Decimal("2650")), (Decimal("1000"), Decimal("1075"), Decimal("200"), Decimal("2824.80"))
_MONTHS = [(month, _EARLY if i < 5 else _LATE) for i, month in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October"])]

CONTRIBUTIONS = {
    "columns": ["SSS", "PhilHealth", "Pag-IBIG", "Withholding tax"],
    "rows": [{"month": month, "amounts": [peso(a) for a in amounts], "total": peso(sum(amounts))} for month, amounts in _MONTHS],
    "totals": [peso(sum(amounts[i] for _, amounts in _MONTHS)) for i in range(4)],
    "grand_total": peso(sum(sum(amounts) for _, amounts in _MONTHS)),
}

RECORDS = {
    "summary": {"name": "Alex M. Rivera", "initials": "AR", "rank": "Assistant Professor",
                "department": "College of Computing", "employee_no": "EMP-0427", "status": "Full-time",
                "since": "Aug 2019"},
    "personal": [
        ("Full name", "Alex M. Rivera"), ("Birth date", "March 14, 1990"), ("Civil status", "Married"),
        ("Address", "12 Sample Street, Barangay Uno, Sample City"), ("Phone", "0918 000 3344"),
        ("Email", "alex.rivera@example.edu"),
    ],
    "emergency": [("Name", "Jordan Rivera"), ("Relationship", "Spouse"), ("Phone", "0917 000 5566")],
    "government_ids": [
        {"id": "gov-sss", "label": "SSS", "full": "34-0000000-1", "masked": "••-•••••••-1"},
        {"id": "gov-philhealth", "label": "PhilHealth", "full": "12-000000000-7", "masked": "••-•••••••••-7"},
        {"id": "gov-pagibig", "label": "Pag-IBIG", "full": "1210-0000-0042", "masked": "••••-••••-0042"},
        {"id": "gov-tin", "label": "TIN", "full": "000-000-000-000", "masked": "•••-•••-•••-000"},
    ],
    "corrections": [
        {"field": "Address", "old": "8 Old Road, Sample City", "new": "12 Sample Street, Barangay Uno, Sample City",
         "filed": "Oct 9", "status": "Pending", "tone": "warning"},
        {"field": "Phone", "old": "0917 000 1122", "new": "0918 000 3344", "filed": "Sep 2", "status": "Approved",
         "tone": "success"},
    ],
    "correction_fields": ["Address", "Phone", "Civil status", "Emergency contact", "Government ID", "Other"],
    "history": [
        {"position": "Assistant Professor", "department": "College of Computing", "grade": "SG 15 · Step 2",
         "dates": "Jun 2024 – present", "current": True, "note": "Step increment"},
        {"position": "Assistant Professor", "department": "College of Computing", "grade": "SG 15 · Step 1",
         "dates": "Jun 2022 – May 2024", "note": "Promotion"},
        {"position": "Instructor", "department": "College of Computing", "grade": "SG 12 · Step 2",
         "dates": "Aug 2021 – May 2022", "note": "Step increment"},
        {"position": "Instructor", "department": "College of Computing", "grade": "SG 12 · Step 1",
         "dates": "Aug 2019 – Jul 2021", "note": "First appointment"},
    ],
    "latest_payslip": PAYSLIPS[0],
    "payslips": PAYSLIPS,
    "contributions": CONTRIBUTIONS,
    "benefits": [
        {"name": "Health card (HMO)", "detail": "Employee and two dependents", "coverage": "Jan 1 – Dec 31, 2026", "icon": "heart"},
        {"name": "Group life insurance", "detail": "Twice the annual basic pay", "coverage": "Since Aug 2019", "icon": "shield-check"},
        {"name": "Dependents' tuition discount", "detail": "50% for up to two children", "coverage": "AY 2026–2027", "icon": "gift"},
        {"name": "Retirement plan", "detail": "Employer matches 5% of basic pay", "coverage": "Since Aug 2024", "icon": "cash"},
    ],
    "documents": [
        {"name": "Appointment: Assistant Professor", "category": "Appointment", "uploaded": "Jun 3, 2022", "size": "PDF · 1.2 MB"},
        {"name": "Appointment: Instructor", "category": "Appointment", "uploaded": "Aug 1, 2019", "size": "PDF · 0.9 MB"},
        {"name": "Master's diploma", "category": "Diploma", "uploaded": "Jul 18, 2021", "size": "PDF · 2.4 MB"},
        {"name": "Bachelor's diploma", "category": "Diploma", "uploaded": "Aug 1, 2019", "size": "PDF · 2.1 MB"},
        {"name": "Training certificate: Outcomes-based teaching", "category": "Certificate", "uploaded": "Mar 22, 2025", "size": "PDF · 0.6 MB"},
    ],
}

BY_PAGE = {"dashboard": DASHBOARD, "records": RECORDS, "attendance": ATTENDANCE}


def for_page(name):
    return BY_PAGE.get(name, {})
