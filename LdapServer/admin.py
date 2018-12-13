from django.contrib import admin

from .models import LdapServer


class LdapServerAdmin(admin.ModelAdmin):
    model = LdapServer
    list_display = ('name','is_active','socket','bind_dn')

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

    def save_model(self, request, obj, form, change):
        super(LdapServerAdmin,self).save_model(request,obj,form,change)

admin.site.register(LdapServer,LdapServerAdmin)