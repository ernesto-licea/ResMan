from django.apps import AppConfig

from CustomUser.signals.signals import create_ldap_user_signal
from LdapServer.ldap.actions import create_ldap_user


class LdapserverConfig(AppConfig):
    name = 'LdapServer'
    verbose_name = 'Active Directory Servers'

    def ready(self):
        create_ldap_user_signal.connect(create_ldap_user,dispatch_uid='create_ldap_user')
