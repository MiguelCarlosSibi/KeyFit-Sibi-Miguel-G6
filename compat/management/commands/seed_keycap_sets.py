from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from compat.models import (
    Brand, KeyDefinition, KeycapProfile, KeycapSet, KeycapSetContent,
    Material, StemType,
)

# Sample/demo catalog data so the checker can be tried straight away.
# Replace or extend it with real, verified sets in the Django admin.

ANSI_60_CONTENTS = {
    "KEY_1U": 70, "MOD_1_25U": 8, "MOD_1_5U": 2, "CAPS_1_75U": 1, "BKSP_2U": 1,
    "ENTER_ANSI": 1, "LSHIFT_ANSI": 1, "RSHIFT_2_75U": 1, "SPACE_6_25U": 1,
}

PROFILES = [("Cherry", "standard"), ("OEM", "standard"), ("Low Profile (Choc)", "low-profile")]
MATERIALS = ["PBT", "ABS"]
BRANDS = ["KeyFit Demo", "Sample Caps Co."]

# (name, brand, keycap profile, material, stem, contents)
SETS = [
    ("Demo Universal Kit", "KeyFit Demo", "Cherry", "PBT", "MX cross", {
        "KEY_1U": 110, "MOD_1_25U": 12, "MOD_1_5U": 4, "CAPS_1_75U": 1, "BKSP_2U": 1,
        "ENTER_ANSI": 1, "ENTER_ISO": 1, "LSHIFT_ANSI": 1, "LSHIFT_ISO": 1,
        "RSHIFT_2_75U": 1, "RSHIFT_1_75U": 1, "SPACE_6_25U": 1, "SPACE_7U": 1}),
    ("Demo Base Kit (7u space)", "Sample Caps Co.", "OEM", "ABS", "MX cross", {
        "KEY_1U": 70, "MOD_1_25U": 8, "MOD_1_5U": 2, "CAPS_1_75U": 1, "BKSP_2U": 1,
        "ENTER_ANSI": 1, "LSHIFT_ANSI": 1, "RSHIFT_2_75U": 1, "SPACE_7U": 1}),
    ("Demo ISO Kit", "KeyFit Demo", "Cherry", "PBT", "MX cross", {
        "KEY_1U": 70, "MOD_1_25U": 8, "MOD_1_5U": 2, "CAPS_1_75U": 1, "BKSP_2U": 1,
        "ENTER_ISO": 1, "LSHIFT_ISO": 1, "RSHIFT_1_75U": 1, "SPACE_6_25U": 1}),
    ("Demo Low-Profile Kit", "Sample Caps Co.", "Low Profile (Choc)", "PBT", "Choc v1",
        ANSI_60_CONTENTS),
    ("Demo Low-Profile MX Set", "KeyFit Demo", "Low Profile (Choc)", "ABS", "MX cross",
        ANSI_60_CONTENTS),
]


class Command(BaseCommand):
    help = "Load sample keycap sets (run seed_reference first; safe to re-run)."

    @transaction.atomic
    def handle(self, *args, **options):
        if not StemType.objects.exists() or not KeyDefinition.objects.exists():
            raise CommandError("Run 'python manage.py seed_reference' first.")

        for name, height in PROFILES:
            KeycapProfile.objects.update_or_create(name=name, defaults={"height_class": height})
        for name in MATERIALS:
            Material.objects.get_or_create(name=name)
        for name in BRANDS:
            Brand.objects.get_or_create(name=name)

        for name, brand, profile, material, stem, contents in SETS:
            keycap_set, _ = KeycapSet.objects.update_or_create(
                brand=Brand.objects.get(name=brand), name=name,
                defaults={
                    "keycap_profile": KeycapProfile.objects.get(name=profile),
                    "material": Material.objects.get(name=material),
                    "stem_type": StemType.objects.get(name=stem),
                    "verification_status": "approved",
                })
            for code, qty in contents.items():
                KeycapSetContent.objects.update_or_create(
                    keycap_set=keycap_set, key_def=KeyDefinition.objects.get(legend_code=code),
                    defaults={"quantity": qty})

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(SETS)} sample keycap sets."))
