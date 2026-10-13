from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_number",
        "title",
        "student",
        "complaint_type",
        "hostel_block",
        "priority",
        "colored_status",
        "created_at",
        "due_at",
        "overdue_flag",
    )
    list_display_links = ("ticket_number", "title")

    list_filter = (
        "status",
        "priority",
        "complaint_type",
        "hostel_block",
        "created_at",
    )

    search_fields = (
        "ticket_number",
        "title",
        "description",
        "student__username",
        "hostel_block",
        "room_number",
    )

    # status yahan se hata diya, kyunki ab badge dikh raha hai.
    # Status change karne ke liye actions ya detail page use karo.
    list_editable = ("priority",)

    readonly_fields = (
        "ticket_number",
        "created_at",
        "resolved_at",
        "due_at",
    )

    list_select_related = ("student",)
    date_hierarchy = "created_at"
    list_per_page = 25
    ordering = ("-created_at",)

    actions = ("mark_in_progress", "mark_resolved", "mark_open")

    # ---------- Custom columns ----------
    @admin.display(description="Status", ordering="status")
    def colored_status(self, obj):
        colors = {
            "Open": "#e74c3c",
            "In Progress": "#f39c12",
            "Resolved": "#27ae60",
        }
        return format_html(
            '<span style="color:#fff;background:{};padding:3px 12px;'
            'border-radius:12px;font-weight:600;font-size:12px;">{}</span>',
            colors.get(obj.status, "#7f8c8d"),
            obj.status,
        )

    @admin.display(description="Overdue", boolean=True)
    def overdue_flag(self, obj):
        value = obj.is_overdue
        return value() if callable(value) else value

    # ---------- Actions ----------
    @admin.action(description="Mark selected as In Progress")
    def mark_in_progress(self, request, queryset):
        count = queryset.update(status="In Progress", resolved_at=None)
        self.message_user(request, f"{count} complaint(s) marked In Progress.")

    @admin.action(description="Mark selected as Resolved")
    def mark_resolved(self, request, queryset):
        count = queryset.update(status="Resolved", resolved_at=timezone.now())
        self.message_user(request, f"{count} complaint(s) marked Resolved.")

    @admin.action(description="Reopen selected complaints")
    def mark_open(self, request, queryset):
        count = queryset.update(status="Open", resolved_at=None)
        self.message_user(request, f"{count} complaint(s) reopened.")


admin.site.site_header = "HostelTrack Admin"
admin.site.site_title = "HostelTrack"
admin.site.index_title = "Complaint Management"