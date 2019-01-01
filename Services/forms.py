from django import forms
from django.utils.translation import gettext_lazy as _


class ServiceForm(forms.ModelForm):
    class Meta:
        fields = "__all__"

    def clean(self):
        cleaned_data = super(ServiceForm, self).clean()
        service_type = cleaned_data.get('service_type')
        email = cleaned_data.get('email')
        if service_type:
            if service_type == 'distribution' and email in ['','None']:
                self.add_error('email',_('If Type of Service is Email Distribution List this field is required.'))
        return cleaned_data