from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Complaint(models.Model):

    TYPE_CHOICES = [
        ("Electricity", "Electricity"),
        ("Water", "Water"),
        ("Internet", "Internet"),
        ("Cleaning", "Cleaning"),
        ("Other", "Other"),
    ]

    STATUS_CHOICES = [
        ("Open", "Open"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
    ]

    PRIORITY_CHOICES = [
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]

    TARGET_HOURS = {
        "Electricity": 4,
        "Water": 4,
        "Internet": 8,
        "Cleaning": 24,
        "Other": 24,
    }

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hostel_complaints",
    )

    ticket_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    title = models.CharField(max_length=150)
    description = models.TextField()
    hostel_block = models.CharField(max_length=80)
    room_number = models.CharField(max_length=30)

    complaint_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
    )

    complaint_date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    target_hours = models.PositiveIntegerField(default=24)
    due_at = models.DateTimeField(null=True, blank=True)

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="Low",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Open",
    )

    staff_note = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_overdue(self):
        return (
            self.status != "Resolved"
            and self.due_at is not None
            and timezone.now() > self.due_at
        )

    def save(self, *args, **kwargs):
        self.target_hours = self.TARGET_HOURS[self.complaint_type]

        if self.complaint_type in ("Electricity", "Water"):
            self.priority = "High"
        elif self.complaint_type == "Internet":
            self.priority = "Medium"
        else:
            self.priority = "Low"

        if self._state.adding:
            self.due_at = timezone.now() + timedelta(
                hours=self.target_hours
            )

        if self.status == "Resolved":
            if self.resolved_at is None:
                self.resolved_at = timezone.now()
        else:
            self.resolved_at = None

        super().save(*args, **kwargs)

        if not self.ticket_number:
            self.ticket_number = f"HT-{self.pk:05d}"
            super().save(update_fields=["ticket_number"])

    def __str__(self):
        return f"{self.ticket_number} - {self.title}"