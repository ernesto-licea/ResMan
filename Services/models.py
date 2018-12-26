from django.db import models
from django.utils.translation import gettext_lazy as _

from Services.signals import signals


class Service(models.Model):
    name = models.CharField(_('name'), max_length=50, default="", unique=True)
    slugname = models.SlugField(_('slugname'),default="")
    description = models.TextField(_('description'),blank=True)

    def __str__(self):
        return self.name

    def create_ldap_service(self):
        signal = getattr(signals, 'create_ldap_service_signal')
        receivers = signal.send_robust(sender=self.__class__, service=self)
        for function, error in receivers:
            return str(error) if error else None

    def modify_ldap_service(self):
        signal = getattr(signals, 'modify_ldap_service_signal')
        receivers = signal.send_robust(sender=self.__class__, service=self)
        for function, error in receivers:
            return str(error) if error else None

    class Meta:
        db_table = 'enterprise_services'
        verbose_name = _('enterprise service')
        verbose_name_plural = _('enterprise services')
