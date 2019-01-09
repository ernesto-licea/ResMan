from django.apps import AppConfig

from CustomUser.signals.signals import save_ldap_user_signal, delete_ldap_user_signal
from LdapServer.ldap.actions import save_ldap_user, save_ldap_group, delete_ldap_group, delete_ldap_user
from Services.signals.signals import save_ldap_group_signal, delete_ldap_group_signal


class LdapserverConfig(AppConfig):
    name = 'LdapServer'
    verbose_name = 'Active Directory Servers'

    def ready(self):
        save_ldap_user_signal.connect(save_ldap_user,dispatch_uid='save_ldap_user')
        save_ldap_group_signal.connect(save_ldap_group,dispatch_uid='save_ldap_group')
        delete_ldap_user_signal.connect(delete_ldap_user,dispatch_uid='delete_ldap_user')
        delete_ldap_group_signal.connect(delete_ldap_group,dispatch_uid='delete_ldap_group')
