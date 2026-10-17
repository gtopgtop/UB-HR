"""Sample data for the prototype screens, passed to templates as context (plan §9.1).

Everything here is invented and generic: no real school, person or department.
PageView merges `for_page(name)` into the context, so pages still make zero database queries.
"""

from .charts import meter, sparkline

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

BY_PAGE = {"dashboard": DASHBOARD}


def for_page(name):
    return BY_PAGE.get(name, {})
