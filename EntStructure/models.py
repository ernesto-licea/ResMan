from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class Area(models.Model):
    is_active = models.BooleanField(_('is active'), default=True)
    name = models.CharField(_('name'), max_length=50, default="", unique=True)
    responsible = models.CharField(_('responsible'), max_length=100, default="", blank=True)
    slugname = models.SlugField(_('slugname'),default="")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'enterprise_areas'
        verbose_name = _('enterprise area')
        verbose_name_plural = _('enterprise areas')

class Department(models.Model):
    is_active = models.BooleanField(_('is active'), default=True)
    area = models.ForeignKey(Area,on_delete=models.CASCADE,verbose_name=_('Area'))
    name = models.CharField(_('name'), max_length=50, default="", unique=True)
    responsible = models.CharField(_('responsible'), max_length=100, default="", blank=True)
    slugname = models.SlugField(_('slugname'),default="")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'enterprise_departments'
        verbose_name = _('enterprise department')
        verbose_name_plural = _('enterprise departments')