"""Compatibility engine for keycap sets (BR-09 to BR-12)."""
from django.db import transaction

from .models import (
    CheckFinding, CheckMissingKey, CompatibilityCheck,
)


@transaction.atomic
def run_keycap_check(profile, keycap_set):
    """Compare a keycap set with a saved board and store the check.

    Incompatible always wins over Partial (BR-09, BR-10). A set that passes
    both is Compatible (BR-11) or Partial with a Missing Keys report (BR-12).
    """
    findings = []
    missing = []

    # BR-09: the stem type must match.
    if keycap_set.stem_type_id != profile.stem_type_id:
        findings.append((
            "STEM_MISMATCH",
            f"The keycap set uses a {keycap_set.stem_type.name} stem, but this "
            f"board accepts {profile.stem_type.name}."))

    # BR-10: the keycap height class must match the board's form factor.
    height_class = keycap_set.keycap_profile.height_class
    if height_class != profile.form_factor:
        findings.append((
            "HEIGHT_CLASS_MISMATCH",
            f"The keycap set is {height_class}, but this board is "
            f"{profile.form_factor}."))

    if findings:
        result = "incompatible"
    else:
        # BR-11 / BR-12: every key the layout needs must be in the set.
        available = {c.key_def_id: c.quantity for c in keycap_set.contents.all()}
        for requirement in profile.layout.requirements.select_related("key_def"):
            have = available.get(requirement.key_def_id, 0)
            if have < requirement.required_qty:
                missing.append((requirement.key_def, requirement.required_qty, have))
        if missing:
            result = "partial"
            findings.append((
                "MISSING_KEYS",
                f"{len(missing)} required key type(s) are short in this set."))
        else:
            result = "compatible"

    check = CompatibilityCheck.objects.create(
        profile=profile, keycap_set=keycap_set, result=result)
    CheckFinding.objects.bulk_create(
        [CheckFinding(compatibility_check=check, reason_code=code, detail=detail)
         for code, detail in findings])
    CheckMissingKey.objects.bulk_create(
        [CheckMissingKey(compatibility_check=check, key_def=key, required_qty=need, available_qty=have)
         for key, need, have in missing])
    return check
