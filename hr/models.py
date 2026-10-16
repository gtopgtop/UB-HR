from django.db import models


# --- Module 1: Employee Profile & Records -----------------------------------

class Department(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    class Role(models.TextChoices):
        TEACHER = "teacher", "Teacher"
        STAFF = "staff", "Staff"
        HR = "hr", "HR Officer"
        ADMIN = "admin", "Administrator"

    employee_no = models.CharField(max_length=12, unique=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    position = models.CharField(max_length=80)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.TEACHER)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees")
    hire_date = models.DateField()
    salary_grade = models.PositiveSmallIntegerField(default=11)

    class Meta:
        ordering = ["last_name", "first_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self):
        return f"{self.first_name[:1]}{self.last_name[:1]}".upper()

    def __str__(self):
        return self.full_name


class CompensationRecord(models.Model):
    """One payslip-style line per employee per pay period."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="compensation")
    period = models.DateField(help_text="First day of the pay period")
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sss = models.DecimalField("SSS/GSIS", max_digits=9, decimal_places=2, default=0)
    philhealth = models.DecimalField("PhilHealth", max_digits=9, decimal_places=2, default=0)
    pagibig = models.DecimalField("Pag-IBIG", max_digits=9, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        ordering = ["-period"]

    @property
    def deductions(self):
        return self.sss + self.philhealth + self.pagibig + self.tax

    @property
    def net_pay(self):
        return self.basic_pay + self.allowances - self.deductions


# --- Module 2: Attendance & Schedule ----------------------------------------

class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        LATE = "late", "Late"
        ABSENT = "absent", "Absent"
        ON_LEAVE = "leave", "On leave"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="attendance")
    date = models.DateField()
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices)

    class Meta:
        ordering = ["-date"]
        unique_together = ("employee", "date")


class LeaveRequest(models.Model):
    class Kind(models.TextChoices):
        VACATION = "vacation", "Vacation"
        SICK = "sick", "Sick"
        EMERGENCY = "emergency", "Emergency"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leave_requests")
    kind = models.CharField(max_length=10, choices=Kind.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ["-start_date"]

    @property
    def days(self):
        return (self.end_date - self.start_date).days + 1


# --- Module 3: Career Development & Performance -----------------------------

class PerformanceEvaluation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="evaluations")
    period = models.CharField(max_length=30, help_text="e.g. SY 2025-2026 Q1")
    score = models.DecimalField(max_digits=3, decimal_places=2, help_text="1.00 - 5.00")
    reviewer = models.CharField(max_length=80)
    feedback = models.TextField(blank=True)
    date = models.DateField()

    class Meta:
        ordering = ["-date"]


class Goal(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="goals")
    title = models.CharField(max_length=120)
    progress = models.PositiveSmallIntegerField(default=0, help_text="0-100")
    due_date = models.DateField()

    class Meta:
        ordering = ["due_date"]


class CareerMilestone(models.Model):
    """Steps in the 'Career Progress Tracker'."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=120)
    order = models.PositiveSmallIntegerField()
    done = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]


# --- Module 4: Communication & Support --------------------------------------

class Announcement(models.Model):
    title = models.CharField(max_length=120)
    body = models.TextField()
    posted_at = models.DateTimeField()
    urgent = models.BooleanField(default=False)

    class Meta:
        ordering = ["-posted_at"]


class ChatMessage(models.Model):
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="received_messages")
    body = models.TextField()
    sent_at = models.DateTimeField()

    class Meta:
        ordering = ["sent_at"]


class ChatbotFAQ(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()


# --- Module 5: Emotional Wellness & Engagement ------------------------------

class MoodCheckIn(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="moods")
    date = models.DateField()
    mood = models.PositiveSmallIntegerField(help_text="1 (low) - 5 (great)")
    stress = models.PositiveSmallIntegerField(help_text="1 (calm) - 5 (overwhelmed)")
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ("employee", "date")


class EngagementSurvey(models.Model):
    title = models.CharField(max_length=120)
    due_date = models.DateField()
    responses = models.PositiveIntegerField(default=0)
    invited = models.PositiveIntegerField(default=0)
    anonymous = models.BooleanField(default=True)

    @property
    def completion(self):
        return round(100 * self.responses / self.invited) if self.invited else 0


# --- Module 6: Admin Dashboard (flagged wellness alerts) --------------------

class WellnessAlert(models.Model):
    class Level(models.TextChoices):
        WATCH = "watch", "Watch"
        HIGH = "high", "High"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="alerts")
    level = models.CharField(max_length=6, choices=Level.choices)
    reason = models.CharField(max_length=200)
    raised_on = models.DateField()
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["resolved", "-raised_on"]
