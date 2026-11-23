from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required

from .check_forms import CheckForm
from .models import CompatibilityCheck, KeyboardProfile, KeycapSet
from .services import run_keycap_check


def _own_checks(request):
    # BR-07: a member only ever sees checks for boards they own.
    return CompatibilityCheck.objects.filter(profile__user=request.user).select_related(
        "profile", "keycap_set__brand")


@login_required
@role_required("member")
def check_create(request):
    initial = {}
    profile_id = request.GET.get("profile", "")
    if profile_id.isdigit():
        initial["profile"] = int(profile_id)
    form = CheckForm(request.POST or None, user=request.user, initial=initial)
    if request.method == "POST":
        if form.is_valid():
            check = run_keycap_check(
                form.cleaned_data["profile"], form.cleaned_data["keycap_set"])
            messages.success(request, "Check complete. Here is your result.")
            return redirect("check_detail", pk=check.pk)
        messages.error(request, "Please fix the errors below.")
    return render(request, "compat/check_form.html", {
        "form": form,
        "has_profiles": KeyboardProfile.objects.filter(user=request.user).exists(),
        "has_sets": KeycapSet.objects.filter(verification_status="approved").exists(),
    })


@login_required
@role_required("member")
def check_list(request):
    return render(request, "compat/check_list.html", {"checks": _own_checks(request)})


@login_required
@role_required("member")
def check_detail(request, pk):
    check = get_object_or_404(
        _own_checks(request).select_related("keycap_set__stem_type", "keycap_set__keycap_profile",
                                            "profile__layout", "profile__stem_type"),
        pk=pk)
    return render(request, "compat/check_detail.html", {
        "check": check,
        "findings": check.findings.all(),
        "missing_keys": check.missing_keys.select_related("key_def"),
    })


@login_required
@role_required("member")
def check_delete(request, pk):
    check = get_object_or_404(_own_checks(request), pk=pk)
    if request.method == "POST":
        check.delete()
        messages.success(request, "Check deleted.")
        return redirect("check_list")
    return render(request, "compat/check_confirm_delete.html", {"check": check})
