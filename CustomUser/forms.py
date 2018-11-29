from django import forms
from django.utils.translation import gettext_lazy as _


class UserFormBase(forms.ModelForm):
    class Meta:
        fields = "__all__"

    def clean(self):
        cleaned_data  = super(UserFormBase, self).clean()
        return cleaned_data


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

    def clean(self):
        cleaned_data  = super(UserFormAdd, self).clean()
        password = cleaned_data.get('password',False)
        retype_password = cleaned_data.get('retype_password',False)

        if password and retype_password:
            if password != retype_password:
                self.add_error('retype_password',_('Passwords do not match.'))

        return cleaned_data

class UserFormEdit(UserFormBase):
    class Meta(UserFormBase.Meta):
        fields = "__all__"

    def clean(self):
        cleaned_data  = super(UserFormBase, self).clean()
        return cleaned_data