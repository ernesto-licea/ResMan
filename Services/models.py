from django.db import models
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    name = models.CharField(_('name'), max_length=50, default="", unique=True)
    slugname = models.SlugField(_('slugname'),default="")
    description = models.TextField(_('description'),blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'enterprise_services'
        verbose_name = _('enterprise service')
        verbose_name_plural = _('enterprise services')
