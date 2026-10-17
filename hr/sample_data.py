"""Sample data for the prototype screens, passed to templates as context (plan §9.1).

Everything here is invented and generic: no real school, person or department.
PageView merges `for_page(name)` into the context, so pages still make zero database queries.
"""

from decimal import Decimal

from .charts import meter, sparkline


def peso(amount):
    return f"₱{amount:,.2f}"


CURRENT_USER = {"name": "Alex Rivera", "first_name": "Alex", "initials": "AR", "role": "Assistant Professor"}

RATING_HISTORY = [("AY 2024–25 S1", 3.9), ("AY 2024–25 S2", 4.1), ("AY 2025–26 S1", 4.2), ("AY 2025–26 S2", 4.4)]

DASHBOARD = {
    "subtitle": "Welcome back, Alex · Monday, October 12 · 1st semester, AY 2026–2027",
    "stats": [
        {"label": "Hours this month", "value": "64 h", "hint": "of 168 h expected", "icon": "calendar-time", "tone": ""},
        {"label": "Leave balance", "value": "15 days", "hint": "9 vacation · 6 sick", "icon": "circle-check", "tone": "t-success"},
        {"label": "Open requests", "value": "1", "hint": "Vacation, awaiting department head", "icon": "clipboard-list", "tone": "t-warning"},
        {"label": "Next evaluation", "value": "Nov 14", "hint": "in 33 days", "icon": "award", "tone": "t-info"},
    ],
    "today": {
        "time_in": "7:48 AM",
        "status": "On time",
        "schedule": [
            {"time": "9:00 – 10:30", "title": "IT 312 Database Systems", "place": "Room 204"},
            {"time": "1:00 – 2:30", "title": "IT 301 Systems Analysis and Design", "place": "Room 305"},
            {"time": "3:00 – 4:00", "title": "Department meeting", "place": "Faculty room"},
        ],
    },
    "career": {
        "current": "Assistant Professor",
        "next": "Associate Professor",
        "steps": [
            {"title": "Instructor", "caption": "2019 – 2022", "state": "done"},
            {"title": "Assistant Professor", "caption": "Current rank", "state": "current"},
            {"title": "Associate Professor", "caption": "Target 2027", "state": "next"},
            {"title": "Professor", "caption": "Later", "state": "next"},
        ],
        "progress": meter(3, 5),
        "requirements": [
            {"label": "Master's degree in a related field", "note": "Done", "done": True},
            {"label": "5 years of teaching experience", "note": "Done · 7 years", "done": True},
            {"label": "Peer evaluation of 4.0 or higher", "note": "Done · 4.2", "done": True},
            {"label": "Research publications", "note": "1 of 2", "done": False},
            {"label": "Community extension hours", "note": "24 of 40 h", "done": False},
        ],
    },
    "rating": {
        "value": "4.4",
        "out_of": "5",
        "delta": "+0.2",
        "delta_period": "vs last semester",
        "trend": sparkline(RATING_HISTORY),
        "raters": [
            {"label": "Student evaluation", "score": "4.5", **meter(4.5, 5)},
            {"label": "Peer evaluation", "score": "4.2", **meter(4.2, 5)},
            {"label": "Supervisor rating", "score": "4.4", **meter(4.4, 5)},
        ],
    },
    "goals": [
        {"title": "Submit one journal article", "due": "Due Dec 15", "note": "50%", **meter(1, 2)},
        {"title": "Advise three capstone groups", "due": "Due Mar 2027", "note": "2 of 3", **meter(2, 3)},
        {"title": "Attend two faculty trainings", "due": "Due Dec 1", "note": "1 of 2", **meter(1, 2)},
        {"title": "Update course syllabi", "due": "Done", "note": "Done", **meter(1, 1)},
    ],
    "moods": ["Low", "Meh", "Okay", "Good", "Great"],
    "leave": [
        {"type": "Vacation leave", **meter(9, 15)},
        {"type": "Sick leave", **meter(6, 10)},
    ],
    "attendance": [
        {"date": "Fri, Oct 9", "hours": "7:55 AM – 5:00 PM", "status": "On time", "tone": "success"},
        {"date": "Thu, Oct 8", "hours": "8:12 AM – 5:05 PM", "status": "Late 12 min", "tone": "warning"},
        {"date": "Wed, Oct 7", "hours": "7:50 AM – 4:58 PM", "status": "On time", "tone": "success"},
        {"date": "Tue, Oct 6", "hours": "7:46 AM – 5:01 PM", "status": "On time", "tone": "success"},
    ],
    "announcements": [
        {"title": "Evaluation schedule for the 1st semester", "kind": "Memo", "date": "Oct 10"},
        {"title": "Updated leave filing guidelines", "kind": "Policy", "date": "Oct 8"},
        {"title": "Faculty wellness seminar, 2:00 PM", "kind": "Event", "date": "Oct 15"},
    ],
    "assistant_prompts": ["How many vacation days do I have?", "Where is my payslip?", "How do I file sick leave?"],
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

BY_PAGE = {"dashboard": DASHBOARD, "records": RECORDS}


def for_page(name):
    return BY_PAGE.get(name, {})
