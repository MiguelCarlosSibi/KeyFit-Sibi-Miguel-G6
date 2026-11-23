from django.contrib import admin

from .models import (
    Brand, CheckFinding, CheckMissingKey, CompatibilityCheck, KeyboardLayout,
    KeyboardProfile, KeyDefinition, KeycapProfile, KeycapSet, KeycapSetContent,
    LayoutKeyRequirement, Material, StemType,
)


class LayoutKeyRequirementInline(admin.TabularInline):
    model = LayoutKeyRequirement
    extra = 0


class KeycapSetContentInline(admin.TabularInline):
    model = KeycapSetContent
    extra = 0


class CheckFindingInline(admin.TabularInline):
    model = CheckFinding
    extra = 0


class CheckMissingKeyInline(admin.TabularInline):
    model = CheckMissingKey
    extra = 0


@admin.register(KeyboardLayout)
class KeyboardLayoutAdmin(admin.ModelAdmin):
    list_display = ("name", "layout_standard", "board_size", "spacebar_size_u")
    inlines = [LayoutKeyRequirementInline]


@admin.register(KeyboardProfile)
class KeyboardProfileAdmin(admin.ModelAdmin):
    list_display = ("profile_name", "user", "layout", "stem_type", "form_factor", "updated_at")
    list_filter = ("form_factor", "socket_type")


@admin.register(KeycapSet)
class KeycapSetAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "keycap_profile", "stem_type", "verification_status")
    list_filter = ("verification_status", "keycap_profile", "stem_type")
    search_fields = ("name", "brand__name")
    inlines = [KeycapSetContentInline]


@admin.register(CompatibilityCheck)
class CompatibilityCheckAdmin(admin.ModelAdmin):
    list_display = ("profile", "keycap_set", "result", "checked_at")
    list_filter = ("result",)
    inlines = [CheckFindingInline, CheckMissingKeyInline]


admin.site.register(StemType)
admin.site.register(KeyDefinition)
admin.site.register(Brand)
admin.site.register(KeycapProfile)
admin.site.register(Material)
