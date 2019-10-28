from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CheckexternaldbConfig(AppConfig):
    name = 'CheckExternalDB'
    verbose_name = _('External DBs to check')
