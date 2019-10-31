from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from CheckExternalDB.signals.signals import externaldb_check_user_signal
from Notification.signal_actions import notification_externaldb_check_user


class NotificationConfig(AppConfig):
    name = 'Notification'
    verbose_name = _('Email Servers')


    def ready(self):
        externaldb_check_user_signal.connect(notification_externaldb_check_user,dispatch_uid='notification_externaldb_check_user')
