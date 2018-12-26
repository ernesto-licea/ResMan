from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
from DistributionList.signals import signals


class DistributionList(models.Model):
    name = models.CharField(_('name'), max_length=50, default="", unique=True)
    responsible = models.CharField(_('responsible'), max_length=100, default="", blank=True)
    email = models.EmailField(_('email area'))
    slugname = models.SlugField(_('slugname'),default="")
    description = models.TextField(_('description'),blank=True)

    def __str__(self):
        return self.name

    def create_ldap_distribution_list(self):
        signal = getattr(signals, 'create_ldap_distribution_list_signal')
        receivers = signal.send_robust(sender=self.__class__, distribution_list=self)
        for function, error in receivers:
            return str(error) if error else None

    def modify_ldap_distribution_list(self):
        signal = getattr(signals, 'modify_ldap_distribution_list_signal')
        receivers = signal.send_robust(sender=self.__class__, distribution_list=self)
        for function, error in receivers:
            return str(error) if error else None

    class Meta:
        db_table = 'enterprise_distribution_list'
        verbose_name = _('enterprise distribution list')
        verbose_name_plural = _('enterprise distribution lists')
