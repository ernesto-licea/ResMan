from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


from .models import LdapServer


class LdapServerAdmin(admin.ModelAdmin):
    model = LdapServer
    list_display = ('name','is_active','socket','bind_dn','server_action')

    fieldsets = (
        (None, {
            'fields': ('is_active','name','server_host','server_port','bind_dn','bind_password')
        }),
        ('Ldap Data Map', {
            'fields': (
                'email_domain','email_buzon_size','email_message_size',
                'proxy_domain','proxy_quota_type','proxy_quota_size','proxy_extra_quota_size'
            ),
        }),
    )

    def get_urls(self):
        urls = super(LdapServerAdmin, self).get_urls()
        custom_urls = [
            url(
                r'^(?P<ldap_server_id>.+)/sync/$',
                self.admin_site.admin_view(self.sync_data),
                name='sync-server',
            ),
        ]
        return custom_urls + urls

    def server_action(self, obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:sync-server', args=[obj.pk]),
            _('sync')
        )

    def sync_data(self,request,ldap_server_id,*args,**kwargs):
        ldap_server = self.get_object(request,ldap_server_id)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)


    def save_model(self, request, obj, form, change):
        super(LdapServerAdmin,self).save_model(request,obj,form,change)

admin.site.register(LdapServer,LdapServerAdmin)