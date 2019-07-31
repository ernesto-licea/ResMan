from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={
            "placeholder":"Username",
            "autocomplete":"off",
            "class":"form-control pb_height-50 reverse",
        }
    ))

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "placeholder":u"Password",
            "autocomplete":"off",
            "class": "form-control pb_height-50 reverse",
        }
    ))

    remember_me = forms.BooleanField(widget=forms.CheckboxInput(),required=False)

class UserPasswordChangeForm(PasswordChangeForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={
            "placeholder": _("New password"),
            "autocomplete": "off",
            "class": "form-control pb_height-50 reverse",
        }),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )

    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "placeholder": _("New password confirmation"),
            "autocomplete": "off",
            "class": "form-control pb_height-50 reverse",
        }),
    )

    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autofocus': True,
            "placeholder": _("Old password"),
            "autocomplete": "off",
            "class": "form-control pb_height-50 reverse",
        }),
    )

    def clean_old_password(self):
        try:
            return super().clean_old_password()
        except forms.ValidationError as e:
            self.fields["old_password"].widget.attrs["class"] = "form-control pb_height-50 reverse is-invalid"
            raise forms.ValidationError(e)

    def clean_new_password2(self):
        try:
            return super().clean_new_password2()
        except forms.ValidationError as e:
            self.fields["new_password2"].widget.attrs["class"] = "form-control pb_height-50 reverse is-invalid"
            raise forms.ValidationError(e)

