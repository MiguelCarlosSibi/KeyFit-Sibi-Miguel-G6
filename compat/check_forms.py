from django import forms

from .models import KeyboardProfile, KeycapSet


class CheckForm(forms.Form):
    profile = forms.ModelChoiceField(
        queryset=KeyboardProfile.objects.none(),
        label="Your board", empty_label="Select one of your saved boards")
    keycap_set = forms.ModelChoiceField(
        queryset=KeycapSet.objects.none(),
        label="Keycap set", empty_label="Select a keycap set")

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        # BR-07: only boards the user owns can be chosen.
        self.fields["profile"].queryset = KeyboardProfile.objects.filter(user=user)
        # BR-15: only approved catalog entries can be checked.
        self.fields["keycap_set"].queryset = KeycapSet.objects.filter(
            verification_status="approved").select_related("brand")
