"""Fill the database with deterministic mock data for the prototype.

    python manage.py seed_mock_data          # wipe + reseed
"""
import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from hr import models as m

DEPARTMENTS = [
    "Elementary", "Junior High", "Senior High", "Guidance",
    "Registrar", "Accounting", "Library", "Administration",
]

# (first, last, position, role, department, salary_grade)
PEOPLE = [
    ("Maria", "Santos", "Senior High Teacher II", "teacher", "Senior High", 14),  # demo employee
    ("Jose", "Reyes", "Elementary Teacher I", "teacher", "Elementary", 11),
    ("Ana", "Dela Cruz", "Elementary Teacher III", "teacher", "Elementary", 15),
    ("Carlo", "Mendoza", "Junior High Teacher II", "teacher", "Junior High", 13),
    ("Liza", "Garcia", "Junior High Teacher I", "teacher", "Junior High", 11),
    ("Paolo", "Villanueva", "Senior High Teacher I", "teacher", "Senior High", 12),
    ("Grace", "Bautista", "Master Teacher I", "teacher", "Senior High", 18),
    ("Mark", "Aquino", "Elementary Teacher II", "teacher", "Elementary", 13),
    ("Joy", "Ramos", "Junior High Teacher III", "teacher", "Junior High", 15),
    ("Ben", "Castillo", "Guidance Counselor", "staff", "Guidance", 14),
    ("Rhea", "Navarro", "Registrar Clerk", "staff", "Registrar", 9),
    ("Tomas", "Flores", "Registrar", "staff", "Registrar", 16),
    ("Nina", "Lopez", "Accountant", "staff", "Accounting", 15),
    ("Ken", "Domingo", "Cashier", "staff", "Accounting", 10),
    ("Ella", "Torres", "Librarian", "staff", "Library", 12),
    ("Rico", "Pascual", "Elementary Teacher I", "teacher", "Elementary", 11),
    ("Sofia", "Manalo", "Junior High Teacher I", "teacher", "Junior High", 11),
    ("Dan", "Salazar", "Senior High Teacher II", "teacher", "Senior High", 13),
    ("Faye", "Cruz", "HR Officer", "hr", "Administration", 16),
    ("Hector", "Ocampo", "HR Assistant", "hr", "Administration", 10),
    ("Dr. Elena", "Marquez", "School Principal", "admin", "Administration", 22),
    ("Vince", "Tan", "Elementary Teacher II", "teacher", "Elementary", 13),
    ("Bea", "Soriano", "Junior High Teacher II", "teacher", "Junior High", 13),
    ("Luis", "Hernandez", "Senior High Teacher I", "teacher", "Senior High", 12),
]

FAQS = [
    ("How many leave credits do I have left?", "You can see your remaining vacation and sick leave credits on the Attendance tab of your home page."),
    ("How do I file a leave request?", "Open Attendance, choose File Leave, pick the type and dates, then submit. Your department head will be notified."),
    ("When is the next payday?", "Salaries are released on the 15th and the last working day of each month."),
    ("What is needed for promotion?", "Your Career Progress Tracker lists every requirement for your next position, with the ones you've completed checked off."),
    ("Who can I talk to about stress or burnout?", "Use the Wellness tab for a daily check-in, or message the Guidance Office. Anonymous feedback is always available."),
]


class Command(BaseCommand):
    help = "Reset and seed the mock HR database."

    @transaction.atomic
    def handle(self, *args, **opts):
        rng = random.Random(2026)
        today = date.today()
        now = timezone.now()

        for model in (
            m.WellnessAlert, m.EngagementSurvey, m.MoodCheckIn, m.ChatbotFAQ, m.ChatMessage,
            m.Announcement, m.CareerMilestone, m.Goal, m.PerformanceEvaluation, m.LeaveRequest,
            m.AttendanceRecord, m.CompensationRecord, m.Employee, m.Department,
        ):
            model.objects.all().delete()

        depts = {n: m.Department.objects.create(name=n) for n in DEPARTMENTS}

        employees = []
        for i, (first, last, pos, role, dept, grade) in enumerate(PEOPLE, start=1):
            employees.append(m.Employee.objects.create(
                employee_no=f"UB-{2015 + i % 9}-{i:03d}",
                first_name=first, last_name=last,
                email=f"{first.split()[-1].lower()}.{last.replace(' ', '').lower()}@ub-school.example",
                phone=f"09{rng.randint(10, 99)}{rng.randint(1000000, 9999999)}",
                position=pos, role=role, department=depts[dept],
                hire_date=today - timedelta(days=rng.randint(300, 3800)),
                salary_grade=grade,
            ))

        workdays = [today - timedelta(days=d) for d in range(0, 45) if (today - timedelta(days=d)).weekday() < 5][:30]

        for emp in employees:
            base = Decimal(18000 + emp.salary_grade * 2100)
            for months_ago in range(6):
                period = (today.replace(day=1) - timedelta(days=30 * months_ago)).replace(day=1)
                m.CompensationRecord.objects.create(
                    employee=emp, period=period, basic_pay=base,
                    allowances=Decimal("1500.00"),
                    sss=(base * Decimal("0.045")).quantize(Decimal("0.01")),
                    philhealth=(base * Decimal("0.025")).quantize(Decimal("0.01")),
                    pagibig=Decimal("200.00"),
                    tax=(base * Decimal("0.06")).quantize(Decimal("0.01")),
                )

            for d in workdays:
                roll = rng.random()
                if roll < 0.82:
                    status, tin = "present", time(7, rng.randint(0, 25))
                elif roll < 0.94:
                    status, tin = "late", time(7, rng.randint(35, 59))
                elif roll < 0.97:
                    status, tin = "leave", None
                else:
                    status, tin = "absent", None
                m.AttendanceRecord.objects.create(
                    employee=emp, date=d, status=status, time_in=tin,
                    time_out=time(17, rng.randint(0, 30)) if tin and d != today else None,
                )

            score = Decimal(str(round(rng.uniform(3.4, 4.9), 2)))
            for q, label in enumerate(["SY 2025-26 Q1", "SY 2025-26 Q2"]):
                m.PerformanceEvaluation.objects.create(
                    employee=emp, period=label, score=min(Decimal("5.00"), score + Decimal(q) / 10),
                    reviewer="Dr. Elena Marquez",
                    feedback=rng.choice([
                        "Consistently well prepared; keep mentoring newer colleagues.",
                        "Strong classroom engagement. Work on timely submission of reports.",
                        "Good progress toward goals. Consider leading a department project.",
                    ]),
                    date=today - timedelta(days=120 - q * 60),
                )

            for title, prog, due in [
                ("Complete 40-hr pedagogy training", rng.randint(30, 100), 60),
                ("Submit action research draft", rng.randint(0, 80), 120),
                ("Mentor one new teacher", rng.randint(10, 90), 200),
            ]:
                m.Goal.objects.create(employee=emp, title=title, progress=prog, due_date=today + timedelta(days=due))

            done_count = rng.randint(1, 4)
            for order, title in enumerate([
                "Meet 3-year service requirement", "Earn 20 PD credits",
                "Rating of Very Satisfactory or better", "Complete master's units", "Submit promotion portfolio",
            ], start=1):
                m.CareerMilestone.objects.create(employee=emp, title=title, order=order, done=order <= done_count)

            leave_status = rng.choice(["approved", "pending", "declined", "approved"])
            m.LeaveRequest.objects.create(
                employee=emp, kind=rng.choice(["vacation", "sick", "emergency"]),
                start_date=today + timedelta(days=rng.randint(3, 25)), end_date=today + timedelta(days=rng.randint(26, 28)),
                reason="Family matters", status=leave_status,
            )

        # Wellness: most people steady, a few trending down so the admin alerts have something to flag.
        struggling = {employees[4], employees[8], employees[13]}
        for emp in employees:
            for d_off in range(21):
                d = today - timedelta(days=d_off)
                if d.weekday() >= 5:
                    continue
                if emp in struggling:
                    mood, stress = rng.randint(1, 3), rng.randint(4, 5)
                else:
                    mood, stress = rng.randint(3, 5), rng.randint(1, 3)
                m.MoodCheckIn.objects.create(employee=emp, date=d, mood=mood, stress=stress)

        for emp, level, reason in [
            (employees[4], "high", "Stress 4+ for 10 consecutive check-ins"),
            (employees[8], "watch", "Mood trending down over 2 weeks"),
            (employees[13], "high", "Three late arrivals plus high stress"),
        ]:
            m.WellnessAlert.objects.create(employee=emp, level=level, reason=reason, raised_on=today - timedelta(days=rng.randint(0, 5)))

        m.EngagementSurvey.objects.create(title="Q4 Workplace Satisfaction", due_date=today + timedelta(days=9), responses=15, invited=len(employees))
        m.EngagementSurvey.objects.create(title="Professional Development Needs", due_date=today + timedelta(days=21), responses=6, invited=len(employees))

        m.Announcement.objects.create(title="Faculty General Assembly", body="Friday, 3:00 PM at the AVR. Attendance is required.", posted_at=now - timedelta(hours=3), urgent=True)
        m.Announcement.objects.create(title="Updated Leave Policy", body="Leave requests must now be filed at least three days in advance except for emergencies.", posted_at=now - timedelta(days=2))
        m.Announcement.objects.create(title="Wellness Week", body="Free counselling slots and yoga sessions all week. Sign up on the Wellness tab.", posted_at=now - timedelta(days=4))

        demo = employees[0]
        hr_officer = next(e for e in employees if e.role == "hr")
        for who, to, text, mins in [
            (hr_officer, demo, "Hi Maria, your salary-grade update was approved.", 190),
            (demo, hr_officer, "Thank you! Could you confirm the effective date?", 170),
            (hr_officer, demo, "Effective first of next month.", 160),
        ]:
            m.ChatMessage.objects.create(sender=who, recipient=to, body=text, sent_at=now - timedelta(minutes=mins))

        for q, a in FAQS:
            m.ChatbotFAQ.objects.create(question=q, answer=a)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {m.Employee.objects.count()} employees, {m.AttendanceRecord.objects.count()} attendance rows, "
            f"{m.MoodCheckIn.objects.count()} mood check-ins. Demo employee: {demo.full_name}"
        ))
