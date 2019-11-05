from django import forms
from django.utils.translation import gettext_lazy as _


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

class LdapServerForm(forms.ModelForm):
    class Meta:
        fields = "__all__"

    def clean(self):
        cleaned_data = super(LdapServerForm, self).clean()
        return cleaned_data

class LdapServerFormAdd(LdapServerForm):

    class Meta(LdapServerForm.Meta):
        widgets = {
            'admin_password': forms.PasswordInput(attrs={'class': 'vTextField'}),
        }

class LdapServerFormEdit(LdapServerForm):
    admin_password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "server's password, but you can change the password using "
            "<a href=\"{}\">this form</a>."
        ),
    )

    class Meta(LdapServerForm.Meta):
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get('admin_password')
        if password:
            password.help_text = password.help_text.format('../ldap_password/')

    def clean_db_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get('db_password')

class SetLdapServerPasswordForm(forms.Form):
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

    def __init__(self, ldap_server, *args, **kwargs):
        self.ldap_server = ldap_server
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
        self.ldap_server.admin_password = password
        if commit:
            self.ldap_server.save()
        return self.ldap_server

