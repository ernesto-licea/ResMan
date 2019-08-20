from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from EntStructure.models import Area
from Services.models import Service


class AreaForm(forms.ModelForm):
    class Meta:
        fields = "__all__"

    def clean_name(self):
        name = self.cleaned_data.get('name',False)
        if name:
            try:
                service = Service.objects.get(name=name)
                raise ValidationError(_("This name is being used by enterprise service"))
            except Service.DoesNotExist:
                pass
        return name