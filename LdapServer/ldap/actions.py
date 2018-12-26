from LdapServer.ldap.models import LdapUser
from django.apps import apps

def create_ldap_user(sender,**kwargs):
    user = kwargs['user']
    appconfig = apps.get_app_config('LdapServer')
    LdapServer = appconfig.get_model('LdapServer','LdapServer')
    ldap_servers = LdapServer.objects.filter(is_active=True)
    for server in ldap_servers:
        ldap_user = LdapUser(server,user)
        ldap_user.add_user()

