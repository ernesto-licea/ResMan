from django import forms
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX, identify_hasher
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _, gettext


class ReadOnlyPasswordHashWidget(forms.Widget):
    template_name = 'auth/widgets/read_only_password_hash.html'
    read_only = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['summary'] = [{'label':_('password'),'value':_('For security reasons this password is hidden')},]
        return context

class ReadOnlyPasswordHashField(forms.Field):
    widget = ReadOnlyPasswordHashWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        super().__init__(*args, **kwargs)

    def bound_data(self, data, initial):
        # Always return initial because the widget doesn't
        # render an input field.
        return initial

    def has_changed(self, initial, data):
        return False

class EmailServerForm(forms.ModelForm):
    class Meta:
        fields = "__all__"

    def clean(self):
        cleaned_data = super(EmailServerForm, self).clean()
        auth_required = cleaned_data.get('auth_required')
        if auth_required:
            email_username = cleaned_data.get('email_username')
            email_password = cleaned_data.get('email_password')
            if not email_username:
                self.add_error('email_username', _('If authentication is required this field can not be empty.'))
            if not email_password:
                self.add_error('email_password', _('If authentication is required this field can not be empty.'))
        return cleaned_data

class EmailServerFormAdd(EmailServerForm):

    class Meta(EmailServerForm.Meta):
        widgets = {
            'email_password': forms.PasswordInput(attrs={'class': 'vTextField'}),
            'retype_password': forms.PasswordInput(attrs={'class': 'vTextField'}),
        }

    def clean(self):
        cleaned_data  = super(EmailServerFormAdd, self).clean()
        return cleaned_data

class EmailServerFormEdit(EmailServerForm):
    email_password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "server's password, but you can change the password using "
            "<a href=\"{}\">this form</a>."
        ),
    )

    class Meta(EmailServerForm.Meta):
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get('email_password')
        if password:
            password.help_text = password.help_text.format('../email_password/')

    def clean(self):
        cleaned_data  = super(EmailServerFormEdit, self).clean()
        return cleaned_data

    def clean_email_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get('email_password')

class SetEmailServerPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
    )
    password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, email_server, *args, **kwargs):
        self.email_server = email_server
        super().__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["password1"]
        self.email_server.email_password = password
        if commit:
            self.email_server.save()
        return self.email_server

