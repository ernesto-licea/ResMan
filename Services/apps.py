from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ServicesConfig(AppConfig):
    name = 'Services'
    verbose_name = _('Enterprise Services')
