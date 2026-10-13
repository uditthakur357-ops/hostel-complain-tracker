import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import FileResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .forms import ComplaintForm
from .models import Complaint


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Account created successfully! Please log in."
            )
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "complaints/register.html", {"form": form})


@login_required
def home(request):
    complaints = Complaint.objects.filter(
        student=request.user
    ).order_by("-created_at")

    query = request.GET.get("q", "").strip()
    selected_type = request.GET.get("type", "")
    selected_status = request.GET.get("status", "")

    if query:
        complaints = complaints.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(ticket_number__icontains=query)
        )

    if selected_type:
        complaints = complaints.filter(complaint_type=selected_type)

    if selected_status:
        complaints = complaints.filter(status=selected_status)

    all_complaints = Complaint.objects.filter(student=request.user)

    context = {
        "complaints": complaints,
        "total_count": all_complaints.count(),
        "resolved_count": all_complaints.filter(status="Resolved").count(),
        "pending_count": all_complaints.exclude(status="Resolved").count(),
        "overdue_count": sum(1 for c in all_complaints if c.is_overdue),
        "search_query": query,
        "selected_type": selected_type,
        "selected_status": selected_status,
        "complaint_types": Complaint.TYPE_CHOICES,
        "priority_choices": Complaint.PRIORITY_CHOICES,
        "status_choices": Complaint.STATUS_CHOICES,
    }

    return render(request, "complaints/home.html", context)


@login_required
def submit_complaint(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST)

        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = request.user
            complaint.save()

            messages.success(
                request,
                f"Complaint submitted! Ticket: {complaint.ticket_number}"
            )
            return redirect("home")
    else:
        form = ComplaintForm()

    return render(
        request,
        "complaints/submit_complaint.html",
        {"form": form}
    )


@login_required
@ensure_csrf_cookie
def frontend_home(request):
    frontend_file = Path(settings.BASE_DIR) / "frontend" / "index.html"

    if not frontend_file.is_file():
        return JsonResponse(
            {"error": "Frontend index.html file was not found."},
            status=404
        )

    return FileResponse(open(frontend_file, "rb"), content_type="text/html")


@login_required
@require_GET
def api_complaints(request):
    complaints = Complaint.objects.filter(
        student=request.user
    ).order_by("-created_at")

    items = [
        {
            "ticket_number": c.ticket_number,
            "title": c.title,
            "description": c.description,
            "category": c.complaint_type,
            "complaint_type": c.complaint_type,
            "hostel_block": c.hostel_block,
            "room_number": c.room_number,
            "priority": c.priority,
            "status": c.status,
            "created_at": c.created_at.strftime("%d %b %Y, %I:%M %p"),
            "is_overdue": c.is_overdue,
        }
        for c in complaints
    ]

    resolved = sum(1 for item in items if item["status"] == "Resolved")

    return JsonResponse({
        "complaints": items,
        "total_count": len(items),
        "pending_count": len(items) - resolved,
        "resolved_count": resolved,
        "overdue_count": sum(1 for item in items if item["is_overdue"]),
        "username": request.user.username,
        "full_name": request.user.get_full_name(),
    })


@login_required
@require_POST
def api_create_complaint(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid request data."}, status=400)

    form = ComplaintForm(data)

    if form.is_valid():
        complaint = form.save(commit=False)
        complaint.student = request.user
        complaint.save()

        return JsonResponse({
            "message": "Complaint submitted successfully!",
            "ticket_number": complaint.ticket_number,
            "status": complaint.status,
        }, status=201)

    return JsonResponse(
        {"errors": form.errors.get_json_data()},
        status=400
    )


@login_required
@require_GET
def api_notifications(request):
    return JsonResponse({"notifications": []})


@login_required
@require_GET
def worker_complaints(request):
    return JsonResponse(
        {"error": "Worker assignment is not configured yet."},
        status=501
    )


@login_required
@require_POST
def api_logout(request):
    logout(request)
    return JsonResponse({"message": "Logged out successfully."})