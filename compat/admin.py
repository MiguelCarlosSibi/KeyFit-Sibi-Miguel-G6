from django.contrib import admin

from .models import (
    KeyboardLayout, KeyboardProfile, KeyDefinition,
    LayoutKeyRequirement, StemType,
)


class LayoutKeyRequirementInline(admin.TabularInline):
    model = LayoutKeyRequirement
    extra = 0


@admin.register(KeyboardLayout)
class KeyboardLayoutAdmin(admin.ModelAdmin):
    list_display = ("name", "layout_standard", "board_size", "spacebar_size_u")
    inlines = [LayoutKeyRequirementInline]


@admin.register(KeyboardProfile)
class KeyboardProfileAdmin(admin.ModelAdmin):
    list_display = ("profile_name", "user", "layout", "stem_type", "form_factor", "updated_at")
    list_filter = ("form_factor", "socket_type")


admin.site.register(StemType)
admin.site.register(KeyDefinition)
