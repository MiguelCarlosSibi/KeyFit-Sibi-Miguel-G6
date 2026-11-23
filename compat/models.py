from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q


# ---------------------------------------------------------------------------
# Reference data (lookup tables and layouts)
# ---------------------------------------------------------------------------

class StemType(models.Model):
    """Stem standard shared by switches, keycaps and boards (e.g. MX cross)."""

    name = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class KeyboardLayout(models.Model):
    """A standard layout a board can have: standard + size + spacebar."""

    STANDARD_CHOICES = [("ANSI", "ANSI"), ("ISO", "ISO")]
    SIZE_CHOICES = [("60%", "60%"), ("65%", "65%"), ("TKL", "TKL"), ("Full", "Full")]

    name = models.CharField(max_length=80, unique=True)
    layout_standard = models.CharField(max_length=4, choices=STANDARD_CHOICES)
    board_size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    spacebar_size_u = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta:
        ordering = ["board_size", "layout_standard", "name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(spacebar_size_u__gt=0), name="layout_spacebar_positive"),
        ]

    def __str__(self):
        return self.name


class KeyDefinition(models.Model):
    """Every distinct keycap size/role a layout may need (e.g. ISO_ENTER)."""

    legend_code = models.CharField(max_length=30, unique=True)
    display_name = models.CharField(max_length=60)
    key_size_u = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta:
        ordering = ["key_size_u", "legend_code"]
        constraints = [
            models.CheckConstraint(
                condition=Q(key_size_u__gt=0), name="key_size_positive"),
        ]

    def __str__(self):
        return self.display_name


class LayoutKeyRequirement(models.Model):
    """Resolves layouts <-> key definitions: which keys a layout needs."""

    layout = models.ForeignKey(
        KeyboardLayout, on_delete=models.CASCADE, related_name="requirements")
    key_def = models.ForeignKey(
        KeyDefinition, on_delete=models.PROTECT, related_name="layout_requirements")
    required_qty = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["layout", "key_def"], name="unique_layout_key"),
            models.CheckConstraint(
                condition=Q(required_qty__gte=1), name="layout_required_qty_min_1"),
        ]

    def __str__(self):
        return f"{self.layout} needs {self.required_qty} x {self.key_def}"


# ---------------------------------------------------------------------------
# Keyboard profiles (a user's saved boards)
# ---------------------------------------------------------------------------

class KeyboardProfile(models.Model):
    MOUNTING_CHOICES = [
        ("tray", "Tray"), ("top", "Top"), ("gasket", "Gasket"),
        ("sandwich", "Sandwich"), ("other", "Other"),
    ]
    SOCKET_CHOICES = [("soldered", "Soldered"), ("hot-swap", "Hot-swap")]
    FORM_FACTOR_CHOICES = [("standard", "Standard"), ("low-profile", "Low-profile")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="keyboard_profiles")
    layout = models.ForeignKey(
        KeyboardLayout, on_delete=models.PROTECT, related_name="profiles")
    stem_type = models.ForeignKey(
        StemType, on_delete=models.PROTECT, related_name="keyboard_profiles")
    profile_name = models.CharField(max_length=60)
    mounting_style = models.CharField(max_length=20, choices=MOUNTING_CHOICES)
    socket_type = models.CharField(max_length=10, choices=SOCKET_CHOICES)
    form_factor = models.CharField(
        max_length=15, choices=FORM_FACTOR_CHOICES, default="standard")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "profile_name"], name="unique_profile_name_per_user"),
        ]

    def __str__(self):
        return self.profile_name


# ---------------------------------------------------------------------------
# Keycap catalog
# ---------------------------------------------------------------------------

class Brand(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class KeycapProfile(models.Model):
    """Keycap profile family (shape and height), e.g. Cherry, OEM, SA."""

    HEIGHT_CHOICES = [("standard", "Standard"), ("low-profile", "Low-profile")]

    name = models.CharField(max_length=40, unique=True)
    height_class = models.CharField(max_length=15, choices=HEIGHT_CHOICES)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=40, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class KeycapSet(models.Model):
    VERIFICATION_CHOICES = [
        ("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"),
    ]

    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="keycap_sets")
    keycap_profile = models.ForeignKey(
        KeycapProfile, on_delete=models.PROTECT, related_name="keycap_sets")
    material = models.ForeignKey(
        Material, on_delete=models.PROTECT, related_name="keycap_sets")
    stem_type = models.ForeignKey(
        StemType, on_delete=models.PROTECT, related_name="keycap_sets")
    verification_status = models.CharField(
        max_length=10, choices=VERIFICATION_CHOICES, default="pending")
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="submitted_keycap_sets")
    source_url_1 = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["brand__name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["brand", "name"], name="unique_set_name_per_brand"),
        ]

    def __str__(self):
        return f"{self.brand} {self.name}"


class KeycapSetContent(models.Model):
    """Resolves keycap sets <-> key definitions: what a set contains."""

    keycap_set = models.ForeignKey(
        KeycapSet, on_delete=models.CASCADE, related_name="contents")
    key_def = models.ForeignKey(
        KeyDefinition, on_delete=models.PROTECT, related_name="set_contents")
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["keycap_set", "key_def"], name="unique_set_key"),
            models.CheckConstraint(
                condition=Q(quantity__gte=1), name="set_content_quantity_min_1"),
        ]

    def __str__(self):
        return f"{self.keycap_set}: {self.quantity} x {self.key_def}"


# ---------------------------------------------------------------------------
# Compatibility checks
# ---------------------------------------------------------------------------

class CompatibilityCheck(models.Model):
    RESULT_CHOICES = [
        ("compatible", "Compatible"),
        ("incompatible", "Incompatible"),
        ("partial", "Partial"),
    ]

    profile = models.ForeignKey(
        KeyboardProfile, on_delete=models.CASCADE, related_name="checks")
    keycap_set = models.ForeignKey(
        KeycapSet, on_delete=models.PROTECT, related_name="checks")
    result = models.CharField(max_length=12, choices=RESULT_CHOICES)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-checked_at", "-pk"]

    def __str__(self):
        return f"{self.profile} vs {self.keycap_set}: {self.result}"


class CheckFinding(models.Model):
    """The reason(s) behind a check result."""

    REASON_CHOICES = [
        ("STEM_MISMATCH", "Stem mismatch"),
        ("HEIGHT_CLASS_MISMATCH", "Height class mismatch"),
        ("MISSING_KEYS", "Missing keys"),
    ]

    compatibility_check = models.ForeignKey(
        CompatibilityCheck, on_delete=models.CASCADE, related_name="findings")
    reason_code = models.CharField(max_length=25, choices=REASON_CHOICES)
    detail = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.reason_code


class CheckMissingKey(models.Model):
    """Snapshot of one key a keycap set is short of for a board."""

    compatibility_check = models.ForeignKey(
        CompatibilityCheck, on_delete=models.CASCADE, related_name="missing_keys")
    key_def = models.ForeignKey(
        KeyDefinition, on_delete=models.PROTECT, related_name="missing_in_checks")
    required_qty = models.PositiveSmallIntegerField()
    available_qty = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["key_def__key_size_u", "key_def__legend_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["compatibility_check", "key_def"], name="unique_missing_key_per_check"),
            models.CheckConstraint(
                condition=Q(required_qty__gte=1), name="missing_required_qty_min_1"),
            models.CheckConstraint(
                condition=Q(available_qty__lt=F("required_qty")),
                name="missing_available_below_required"),
        ]

    @property
    def short_by(self):
        return self.required_qty - self.available_qty

    def __str__(self):
        return f"{self.key_def}: {self.available_qty}/{self.required_qty}"
