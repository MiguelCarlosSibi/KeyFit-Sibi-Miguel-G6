from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .decorators import role_required
from .forms import ProfileForm, RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. You can now log in.")
            return redirect("login")
        messages.error(request, "Please fix the errors below.")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    if request.user.role == "admin":
        return redirect("admin_dashboard")
    return redirect("member_dashboard")


@login_required
@role_required("member")
def member_dashboard(request):
    return render(request, "accounts/member_dashboard.html")


@login_required
@role_required("admin")
def admin_dashboard(request):
    return render(request, "accounts/admin_dashboard.html")


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
        messages.error(request, "Please fix the errors below.")
    return render(request, "accounts/profile.html", {"form": form})
