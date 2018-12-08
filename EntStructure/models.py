from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class Area(models.Model):
    name = models.CharField(_('name'), max_length=50, default="", unique=True)
    responsible = models.CharField(_('responsible'), max_length=100, default="", blank=True)
    email = models.EmailField(_('email area'))

    class Meta:
        db_table = 'enterprise_areas'
        verbose_name = _('enterprise area')
        verbose_name_plural = _('enterprise areas')