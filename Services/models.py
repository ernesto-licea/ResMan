from django.db import models
from django.utils.translation import gettext_lazy as _

class Service(models.Model):
    SERVICE_TYPE = [
        ('security',_('Service')),
        ('distribution', _('Email Distribution List'))
    ]

    is_active = models.BooleanField(_('is active'), default=True)
    name = models.CharField(_('name'), max_length=100, default="", unique=True)
    service_type = models.CharField(_('Type of Service'),choices=SERVICE_TYPE,default=SERVICE_TYPE[0][0],max_length=20)
    email = models.EmailField(_('email'), default="", blank=True)
    description = models.TextField(_('Description'),blank=True)
    slugname = models.SlugField(_('slugname'),blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'services'
        verbose_name = _('service')
        verbose_name_plural = _('services')
