from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required

from .forms import MAX_PROFILES, KeyboardProfileForm
from .models import KeyboardProfile


def _own_profiles(request):
    # BR-07: a member only ever sees profiles they own.
    return KeyboardProfile.objects.filter(user=request.user).select_related(
        "layout", "stem_type")


@login_required
@role_required("member")
def profile_list(request):
    return render(request, "compat/profile_list.html", {
        "profiles": _own_profiles(request),
        "max_profiles": MAX_PROFILES,
    })


@login_required
@role_required("member")
def profile_create(request):
    form = KeyboardProfileForm(request.POST or None, user=request.user)
    if request.method == "POST":
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, f'Board "{profile.profile_name}" saved.')
            return redirect("profile_list")
        messages.error(request, "Please fix the errors below.")
    return render(request, "compat/profile_form.html", {
        "form": form, "title": "Add a keyboard board", "submit_label": "Save board",
    })


@login_required
@role_required("member")
def profile_edit(request, pk):
    profile = get_object_or_404(_own_profiles(request), pk=pk)
    form = KeyboardProfileForm(
        request.POST or None, instance=profile, user=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, f'Board "{profile.profile_name}" updated.')
            return redirect("profile_list")
        messages.error(request, "Please fix the errors below.")
    return render(request, "compat/profile_form.html", {
        "form": form, "title": f"Edit {profile.profile_name}",
        "submit_label": "Save changes",
    })


@login_required
@role_required("member")
def profile_delete(request, pk):
    profile = get_object_or_404(_own_profiles(request), pk=pk)
    if request.method == "POST":
        name = profile.profile_name
        profile.delete()
        messages.success(request, f'Board "{name}" deleted.')
        return redirect("profile_list")
    return render(request, "compat/profile_confirm_delete.html", {"profile": profile})
