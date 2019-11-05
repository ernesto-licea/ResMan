import base64

from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import quote, unquote
from django.contrib.auth.admin import sensitive_post_parameters_m
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils.html import format_html, escape
from django.utils.http import urlquote
from django.utils.translation import gettext_lazy as _, gettext
from CustomUser.models import UserEnterprise, UserInstitutional, UserGuest
from LdapServer.forms import LdapServerFormEdit, LdapServerFormAdd, SetLdapServerPasswordForm
from ResMan.admin import admin_site
from Services.models import Service
from .models import LdapServer

def change_password(modeladmin,request, id, form_url=''):
    if not modeladmin.has_change_permission(request):
        raise PermissionDenied
    ldap_server = modeladmin.get_object(request, unquote(id))
    if ldap_server is None:
        raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
            'name': modeladmin.model._meta.verbose_name,
            'key': escape(id),
        })
    if request.method == 'POST':
        form = SetLdapServerPasswordForm(ldap_server, request.POST)
        if form.is_valid():

            admin_password = form.cleaned_data.get('password1')
            ldap_server = form.save(commit=False)
            ldap_server.admin_password = base64.b64encode(admin_password.encode('utf-8')).decode()
            ldap_server.save()

            change_message = modeladmin.construct_change_message(request, form, None)
            modeladmin.log_change(request, ldap_server, change_message)

            msg = gettext('Password changed successfully.')
            messages.success(request, msg)

            return HttpResponseRedirect(
                reverse(
                    '%s:%s_%s_changelist' % (
                        modeladmin.admin_site.name,
                        ldap_server._meta.app_label,
                        ldap_server._meta.model_name,
                ))
            )
    else:
        form = SetLdapServerPasswordForm(ldap_server)

    fieldsets = [(None, {'fields': list(form.base_fields)})]
    adminForm = admin.helpers.AdminForm(form, fieldsets, {})

    context = {
        'title': _('Change password: %s') % escape(ldap_server.name),
        'adminForm': adminForm,
        'form_url': form_url,
        'form': form,
        'is_popup': (IS_POPUP_VAR in request.POST or
                     IS_POPUP_VAR in request.GET),
        'add': True,
        'change': False,
        'has_delete_permission': False,
        'has_change_permission': True,
        'has_absolute_url': False,
        'opts': modeladmin.model._meta,
        'original': ldap_server,
        'save_as': False,
        'show_save': True,
        **modeladmin.admin_site.each_context(request),
    }

    request.current_app = modeladmin.admin_site.name

    return TemplateResponse(
        request,
        'LdapServer/change_password.html',
        context,
    )

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

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            kwargs['form'] = LdapServerFormEdit
        else:
            kwargs['form'] = LdapServerFormAdd
        return super().get_form(request, obj, **kwargs)

    def get_urls(self):
        urls = super(LdapServerAdmin, self).get_urls()
        custom_urls = [
            path(
                '<id>/ldap_password/',
                self.admin_site.admin_view(self.server_password_change),
                name='server_password_change',
            ),
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

    @sensitive_post_parameters_m
    def server_password_change(self, request, id, form_url=''):
        return change_password(self, request, id, form_url)

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
        if not change:
            obj.admin_password = base64.b64encode(obj.admin_password.encode('utf-8')).decode()
        super(LdapServerAdmin,self).save_model(request,obj,form,change)

admin_site.register(LdapServer,LdapServerAdmin)