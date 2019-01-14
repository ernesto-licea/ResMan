from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.utils import quote
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlquote
from django.utils.translation import gettext_lazy as _


from .models import LdapServer


class LdapServerAdmin(admin.ModelAdmin):
    model = LdapServer
    list_display = ('name','is_active','socket','admin_username','server_action')

    fieldsets = (
        (None, {
            'fields': ('is_active','name','domain','search_base','server_host','server_port','start_tls','admin_username','admin_password')
        }),
        ('Ldap Data Map', {
            'fields': (
                'email_domain','email_buzon_size','email_message_size',
                'internet_domain','internet_quota_type','internet_quota_size','internet_extra_quota_size',
                'ftp_home','ftp_size'
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
            url(
                r'^(?P<ldap_server_id>.+)/test_connection/$',
                self.admin_site.admin_view(self.test_server),
                name='test-server',
            ),
        ]
        return custom_urls + urls

    def server_action(self, obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:sync-server', args=[obj.pk]),
            _('sync')
        ) + format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:test-server', args=[obj.pk]),
            _('Test Connection')
        )

    def sync_data(self,request,ldap_server_id,*args,**kwargs):
        obj = self.get_object(request,ldap_server_id)

        self.message_user(request, self._sync_message(obj), messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def _sync_message(self,obj):
        opts = obj._meta

        # Construct message to return
        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,
        )
        obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)
        message = format_html(
            _("Data was sent to server {} successfully."),
            obj_repr
        )
        return message

    def test_server(self,request,ldap_server_id,*args,**kwargs):
        ldap_server = self.get_object(request,ldap_server_id)
        opts = ldap_server._meta

        #Construct message to return
        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(ldap_server.pk),),
            current_app=self.admin_site.name,
        )
        obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), ldap_server)
        message = format_html(
            _("Connection to server {} was successfully established."),
              obj_repr
        )
        self.message_user(request, message, messages.SUCCESS)


        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)


    def save_model(self, request, obj, form, change):
        super(LdapServerAdmin,self).save_model(request,obj,form,change)

admin.site.register(LdapServer,LdapServerAdmin)