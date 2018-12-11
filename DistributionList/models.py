from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class DistributionList(models.Model):
    name = models.CharField(_('name'), max_length=50, default="", unique=True)
    responsible = models.CharField(_('responsible'), max_length=100, default="", blank=True)
    email = models.EmailField(_('email area'))
    slugname = models.SlugField(_('slugname'),default="")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'enterprise_distribution_list'
        verbose_name = _('enterprise distribution list')
        verbose_name_plural = _('enterprise distribution lists')