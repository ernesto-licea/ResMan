from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from EntStructure.models import Area


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

    def clean_name(self):
        name = self.cleaned_data.get('name',False)
        if name:
            try:
                area = Area.objects.get(name=name)
                raise ValidationError(_("This name is being used by Enterprise Area"))
            except Area.DoesNotExist:
                pass
        return name