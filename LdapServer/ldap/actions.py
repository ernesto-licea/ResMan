from LdapServer.ldap.models import LdapUser
from LdapServer.models import LdapServer


def create_ldap_server(sender,**kwargs):
    user = kwargs['user']
    ldap_servers = LdapServer.objects.filter(is_active=True)
    for server in ldap_servers:
        ldap_user = LdapUser(server,user)
        ldap_user.add_user()

