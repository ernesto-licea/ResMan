from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.utils import quote
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlquote
from django.utils.translation import gettext_lazy as _

from CustomUser.models import UserEnterprise, UserInstitutional, UserGuest
from ResMan.admin import admin_site
from Services.models import Service
from .models import LdapServer


class LdapServerAdmin(admin.ModelAdmin):
    model = LdapServer
    list_display = ('name','is_active','socket','admin_username','server_action')

    fieldsets = (
        (None, {
            'fields': ('is_active','name','domain_name','domain','search_base','server_host','server_port','start_tls','admin_username','admin_password')
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
    server_action.short_description = _("Server Actions")

    def sync_data(self,request,ldap_server_id,*args,**kwargs):
        obj = self.get_object(request,ldap_server_id)

        error_list = []
        services_list = Service.objects.filter(is_active=True)

        for service in services_list:
            ldap_error = service.ldap_save(obj)
            if ldap_error:
                error_list.append(ldap_error)

        enterprise_user_list = UserEnterprise.objects.all()

        for user in enterprise_user_list:
            user._password = user.session
            ldap_error = user.ldap_save(obj)
            if ldap_error:
                error_list.append(ldap_error)

        institutional_user_list = UserInstitutional.objects.all()

        for user in institutional_user_list:
            user._password = user.session
            ldap_error = user.ldap_save(obj)
            if ldap_error:
                error_list.append(ldap_error)

        guest_user_list = UserGuest.objects.all()

        for user in guest_user_list:
            user._password = user.session
            ldap_error = user.ldap_save(obj)
            if ldap_error:
                error_list.append(ldap_error)

        if error_list:
            for error in error_list:
                self.message_user(request,error,messages.ERROR)
        else:
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

        testuser = UserGuest(
            status= 'active',
            username='testuser',
            first_name= 'TestUser',
            last_name= 'TestUser',
            email_domain='local',
            internet_quota_type='daily',
            internet_domain='local'
        )
        testuser.save()
        testuser._password = "AdminAdmin999*"

        ldap_error = testuser.ldap_save(ldap_server)

        if ldap_error:
            self.message_user(request,ldap_error,messages.ERROR)
            testuser.delete()
        else:
            testuser.delete()
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

admin_site.register(LdapServer,LdapServerAdmin)