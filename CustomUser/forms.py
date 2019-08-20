import re

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX, identify_hasher
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _, gettext

from Services.models import Service


class ReadOnlyPasswordHashWidget(forms.Widget):
    template_name = 'auth/widgets/read_only_password_hash.html'
    read_only = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        summary = []
        if not value or value.startswith(UNUSABLE_PASSWORD_PREFIX):
            summary.append({'label': gettext("No password set.")})
        else:
            try:
                hasher = identify_hasher(value)
            except ValueError:
                summary.append({'label': gettext("Invalid password format or unknown hashing algorithm.")})
            else:
                for key, value_ in hasher.safe_summary(value).items():
                    summary.append({'label': gettext(key), 'value': value_})
        context['summary'] = summary
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


class UserFormBase(forms.ModelForm):
    class Meta:
        fields = "__all__"

    def clean(self):
        cleaned_data  = super(UserFormBase, self).clean()
        services = cleaned_data.get('services')
        if services:
            exist_email_service = services.filter(name='Email').count() > 0
            exist_internet_service = services.filter(name='Internet').count() > 0
            exist_ftp_service = services.filter(name='Ftp').count() > 0

            email_error_message = _('If you select email service this field is required.')
            email_field = ['email','email_domain','email_buzon_size','email_message_size']
            for field in email_field:
                data = str(cleaned_data.get(field))
                if data in ["","None"] and exist_email_service:
                    self.add_error(field, email_error_message)

            internet_error_message = _('If you select internet service this field is required.')
            internet_field = ['internet_domain','internet_quota_type','internet_quota_size','internet_extra_quota_size']
            for field in internet_field:
                data = str(cleaned_data.get(field))
                if data in ["", "None"] and exist_internet_service:
                    self.add_error(field, internet_error_message)

            ftp_error_message = _('If you select ftp service this field is required.')
            ftp_fields = ['ftp_folder','ftp_size']
            for field in ftp_fields:
                data = str(cleaned_data.get(field))
                if data in ["", "None"] and exist_ftp_service:
                    self.add_error(field, ftp_error_message)


        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            try:
                service = Service.objects.get(name=username)
                raise ValidationError(_("This username is being used as Service name."))
            except Service.DoesNotExist:
                pass
        return username


    def clean_ci_number(self):
        ci_number = self.cleaned_data.get('ci_number')
        if ci_number:
            pattern = re.compile('\d{11}$')
            if not pattern.match(ci_number):
                raise ValidationError(_('Invalid ci number.'))
        return ci_number

    def clean_enterprise_number(self):
        enterprise_number = self.cleaned_data.get('enterprise_number')
        if enterprise_number:
            pattern = re.compile('\d+$')
            if not pattern.match(enterprise_number):
                raise ValidationError(_('Invalid enterprise number.'))
        return enterprise_number

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            pattern = re.compile('[0-9,-]+$')
            pattern2 = re.compile('.*--.*')
            if not pattern.match(phone_number) or pattern2.match(phone_number) or not phone_number[-1].isdigit() or not phone_number[0].isdigit():
                raise ValidationError(_('Invalid phone number.'))
        return phone_number

    def clean_extension_number(self):
        extension_number = self.cleaned_data.get('extension_number')
        if extension_number:
            pattern = re.compile('\d+$')
            if not pattern.match(extension_number):
                raise ValidationError(_('Invalid extension number.'))
        return extension_number

    def clean_email(self):
        email = self.cleaned_data.get('email',False)
        if email:
            try:
                service = Service.objects.get(email=email)
                raise ValidationError(_("This email is being used by enterprise service or distribution list"))
            except Service.DoesNotExist:
                pass
        return email




class UserFormAdd(UserFormBase):
    retype_password = forms.CharField(
        label=_('Retype Password'),
        widget=forms.PasswordInput(attrs={'class':'vTextField'}),
        max_length=150,
        help_text=_('Confirm the previous password.')
    )

    class Meta(UserFormBase.Meta):
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'vTextField'}),
            'retype_password': forms.PasswordInput(attrs={'class': 'vTextField'}),
        }

    def clean_retype_password(self):
        password2 = self.cleaned_data.get('retype_password')
        if password2:
            password_validation.validate_password(password2)
        return password2

    def clean(self):
        cleaned_data  = super(UserFormAdd, self).clean()
        password = cleaned_data.get('password',False)
        retype_password = cleaned_data.get('retype_password',False)

        if password and retype_password:
            if password != retype_password:
                self.add_error('retype_password',_('Passwords do not match.'))

        return cleaned_data

class UserFormEdit(UserFormBase):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"{}\">this form</a>."
        ),
    )

    class Meta(UserFormBase.Meta):
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get('password')
        if password:
            password.help_text = password.help_text.format('../password/')

    def clean(self):
        cleaned_data  = super(UserFormEdit, self).clean()
        return cleaned_data

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get('password')