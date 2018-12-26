from LdapServer.ldap.models import LdapUser, LdapSecurityGroup
from django.apps import apps

appconfig = apps.get_app_config('LdapServer')
LdapServer = appconfig.get_model('LdapServer','LdapServer')


def create_ldap_user(sender,**kwargs):
    user = kwargs['user']
    ldap_servers = LdapServer.objects.filter(is_active=True)
    for server in ldap_servers:
        ldap_user = LdapUser(server,user)
        ldap_user.add_user()

def create_ldap_security_group(sender,**kwargs):
    service = kwargs['service']
    ldap_servers = LdapServer.objects.filter(is_active=True)
    for server in ldap_servers:
        ldap_user = LdapSecurityGroup(server,service)
        ldap_user.add()

