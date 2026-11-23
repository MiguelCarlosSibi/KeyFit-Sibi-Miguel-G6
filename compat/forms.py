from django import forms

from .models import KeyboardLayout, KeyboardProfile

MAX_PROFILES = 10  # BR-04


class KeyboardProfileForm(forms.ModelForm):
    class Meta:
        model = KeyboardProfile
        fields = [
            "profile_name", "layout", "stem_type",
            "mounting_style", "socket_type", "form_factor",
        ]
        labels = {
            "profile_name": "Board name",
            "layout": "Layout (standard, size, spacebar)",
            "stem_type": "Stem type the board's sockets accept",
            "mounting_style": "Mounting style",
            "socket_type": "Socket type",
            "form_factor": "Form factor",
        }
        help_texts = {
            "profile_name": "A name only you will see, e.g. \"My 65% daily\".",
            "mounting_style": "Saved for your reference; not used by the checks yet.",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["layout"].queryset = KeyboardLayout.objects.all()
        self.fields["layout"].empty_label = "Select a layout"
        self.fields["stem_type"].empty_label = "Select a stem type"

    def clean_profile_name(self):
        name = self.cleaned_data["profile_name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Board name must be at least 2 characters.")
        # BR-05: unique among this user's profiles (case-insensitive)
        duplicates = KeyboardProfile.objects.filter(
            user=self.user, profile_name__iexact=name)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("You already have a board with this name.")
        return name

    def clean(self):
        cleaned = super().clean()
        # BR-04: at most MAX_PROFILES saved boards per user
        if not self.instance.pk and self.user is not None:
            if KeyboardProfile.objects.filter(user=self.user).count() >= MAX_PROFILES:
                raise forms.ValidationError(
                    f"You can save at most {MAX_PROFILES} boards. "
                    "Delete one before adding another.")
        return cleaned
