from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.frontend_home, name="home"),

    path("register/", views.register, name="register"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="complaints/login.html"
        ),
        name="login",
    ),

    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path(
        "submit-complaint/",
        views.submit_complaint,
        name="submit_complaint",
    ),

    path("api/complaints/", views.api_complaints, name="api_complaints"),
    path("api/complaints/create/", views.api_create_complaint, name="api_create_complaint"),
    path("api/logout/", views.api_logout, name="api_logout"),
]