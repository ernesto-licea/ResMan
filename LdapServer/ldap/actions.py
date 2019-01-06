from django.contrib.admin.utils import quote
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlquote

from LdapServer.ldap.models import LdapUser, LdapGroup
from django.apps import apps
from django.utils.translation import gettext_lazy as _



def save_ldap_user(sender,**kwargs):
    user = kwargs['obj']
    appconfig = apps.get_app_config('LdapServer')
    LdapServer = appconfig.get_model('LdapServer', 'LdapServer')
    ldap_servers = LdapServer.objects.filter(is_active=True)
    for server in ldap_servers:
        ldap_user = LdapUser(server,user)
        try:
            ldap_user.save()
        except Exception as e:
            opts = server._meta
            # Construct message to return
            obj_url = reverse(
                'admin:%s_%s_change' % (opts.app_label, opts.model_name),
                args=(quote(server.pk),),
            )
            obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), server)
            message = format_html(
                _("Active Directory {} says: {}."),
                obj_repr,
                e
            )
            raise Exception(message)

def save_ldap_group(sender,**kwargs):
    service = kwargs['obj']
    appconfig = apps.get_app_config('LdapServer')
    LdapServer = appconfig.get_model('LdapServer', 'LdapServer')
    ldap_servers = LdapServer.objects.filter(is_active=True)
    for server in ldap_servers:
        ldap_group = LdapGroup(server,service)
        ldap_group.save()
