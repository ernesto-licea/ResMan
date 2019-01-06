from LdapServer.ldap.models import LdapUser, LdapGroup
from django.apps import apps



def save_ldap_user(sender,**kwargs):
    user = kwargs['user']
    appconfig = apps.get_app_config('LdapServer')
    LdapServer = appconfig.get_model('LdapServer', 'LdapServer')
    ldap_servers = LdapServer.objects.filter(is_active=True)
    for server in ldap_servers:
        ldap_user = LdapUser(server,user)
        ldap_user.save()

def save_ldap_group(sender,**kwargs):
    service = kwargs['obj']
    appconfig = apps.get_app_config('LdapServer')
    LdapServer = appconfig.get_model('LdapServer', 'LdapServer')
    ldap_servers = LdapServer.objects.filter(is_active=True)
    for server in ldap_servers:
        ldap_group = LdapGroup(server,service)
        ldap_group.save()
