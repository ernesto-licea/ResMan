from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class Area(models.Model):
    name = models.CharField(_('name'), max_length=50, default="", unique=True)
    responsible = models.CharField(_('responsible'), max_length=100, default="", blank=True)
    email = models.EmailField(_('email area'))

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'enterprise_areas'
        verbose_name = _('enterprise area')
        verbose_name_plural = _('enterprise areas')

class Department(models.Model):
    area = models.ForeignKey(Area,on_delete=models.CASCADE)
    name = models.CharField(_('name'), max_length=50, default="", unique=True)
    responsible = models.CharField(_('responsible'), max_length=100, default="", blank=True)
    email = models.EmailField(_('email area'))

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'enterprise_departments'
        verbose_name = _('enterprise department')
        verbose_name_plural = _('enterprise departments')