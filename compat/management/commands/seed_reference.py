from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from compat.models import (
    KeyboardLayout, KeyDefinition, LayoutKeyRequirement, StemType,
)

STEMS = [
    ("MX cross", "Cherry MX-style cross stem, the most common standard."),
    ("Choc v1", "Kailh Choc v1 stem used by low-profile boards."),
    ("Alps", "Alps-style stem. Limited coverage."),
]

# (legend_code, display_name, size in units)
KEYS = [
    ("KEY_1U", "1u standard key", "1.00"),
    ("MOD_1_25U", "1.25u modifier", "1.25"),
    ("MOD_1_5U", "1.5u key (Tab / backslash)", "1.50"),
    ("CAPS_1_75U", "1.75u Caps Lock", "1.75"),
    ("BKSP_2U", "2u Backspace", "2.00"),
    ("ENTER_ANSI", "ANSI Enter (2.25u)", "2.25"),
    ("ENTER_ISO", "ISO Enter", "1.25"),
    ("LSHIFT_ANSI", "ANSI Left Shift (2.25u)", "2.25"),
    ("LSHIFT_ISO", "ISO Left Shift (1.25u)", "1.25"),
    ("RSHIFT_2_75U", "Right Shift 2.75u", "2.75"),
    ("RSHIFT_1_75U", "Right Shift 1.75u", "1.75"),
    ("SPACE_6_25U", "6.25u Spacebar", "6.25"),
    ("SPACE_7U", "7u Spacebar", "7.00"),
]

# (name, standard, size, spacebar_u, {legend_code: required quantity})
# Quantities are typical counts for each layout.
LAYOUTS = [
    ("60% ANSI (6.25u space)", "ANSI", "60%", "6.25", {
        "KEY_1U": 46, "MOD_1_25U": 7, "MOD_1_5U": 2, "CAPS_1_75U": 1,
        "BKSP_2U": 1, "ENTER_ANSI": 1, "LSHIFT_ANSI": 1,
        "RSHIFT_2_75U": 1, "SPACE_6_25U": 1}),
    ("65% ANSI (6.25u space)", "ANSI", "65%", "6.25", {
        "KEY_1U": 55, "MOD_1_25U": 3, "MOD_1_5U": 2, "CAPS_1_75U": 1,
        "BKSP_2U": 1, "ENTER_ANSI": 1, "LSHIFT_ANSI": 1,
        "RSHIFT_1_75U": 1, "SPACE_6_25U": 1}),
    ("65% ISO (6.25u space)", "ISO", "65%", "6.25", {
        "KEY_1U": 57, "MOD_1_25U": 3, "MOD_1_5U": 1, "CAPS_1_75U": 1,
        "BKSP_2U": 1, "ENTER_ISO": 1, "LSHIFT_ISO": 1,
        "RSHIFT_1_75U": 1, "SPACE_6_25U": 1}),
    ("TKL ANSI (6.25u space)", "ANSI", "TKL", "6.25", {
        "KEY_1U": 72, "MOD_1_25U": 7, "MOD_1_5U": 2, "CAPS_1_75U": 1,
        "BKSP_2U": 1, "ENTER_ANSI": 1, "LSHIFT_ANSI": 1,
        "RSHIFT_2_75U": 1, "SPACE_6_25U": 1}),
]


class Command(BaseCommand):
    help = "Load stem types, key definitions and keyboard layouts (safe to re-run)."

    @transaction.atomic
    def handle(self, *args, **options):
        for name, description in STEMS:
            StemType.objects.update_or_create(
                name=name, defaults={"description": description})

        keys = {}
        for code, display, size in KEYS:
            keys[code], _ = KeyDefinition.objects.update_or_create(
                legend_code=code,
                defaults={"display_name": display, "key_size_u": Decimal(size)})

        for name, standard, size, space, requirements in LAYOUTS:
            layout, _ = KeyboardLayout.objects.update_or_create(
                name=name,
                defaults={"layout_standard": standard, "board_size": size,
                          "spacebar_size_u": Decimal(space)})
            for code, qty in requirements.items():
                LayoutKeyRequirement.objects.update_or_create(
                    layout=layout, key_def=keys[code],
                    defaults={"required_qty": qty})

        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(STEMS)} stem types, {len(KEYS)} key definitions, "
            f"{len(LAYOUTS)} layouts."))
