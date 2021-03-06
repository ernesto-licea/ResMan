import base64
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import quote, unquote
from django.contrib.auth.admin import sensitive_post_parameters_m
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.http import HttpResponseRedirect, Http404
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils.html import format_html, escape
from django.utils.http import urlquote

from Notification.forms import EmailServerFormAdd, EmailServerFormEdit, SetEmailServerPasswordForm
from Notification.models import EmailServer
from ResMan.admin import admin_site
from django.utils.translation import gettext_lazy as _, gettext


def change_password(modeladmin,request, id, form_url=''):
    if not modeladmin.has_change_permission(request):
        raise PermissionDenied
    email_server = modeladmin.get_object(request, unquote(id))
    if email_server is None:
        raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
            'name': modeladmin.model._meta.verbose_name,
            'key': escape(id),
        })
    if request.method == 'POST':
        form = SetEmailServerPasswordForm(email_server, request.POST)
        if form.is_valid():

            email_password = form.cleaned_data.get('password1')
            email_server = form.save(commit=False)
            email_server.email_password = base64.b64encode(email_password.encode('utf-8')).decode()
            email_server.save()

            change_message = modeladmin.construct_change_message(request, form, None)
            modeladmin.log_change(request, email_server, change_message)

            msg = gettext('Password changed successfully.')
            messages.success(request, msg)

            return HttpResponseRedirect(
                reverse(
                    '%s:%s_%s_changelist' % (
                        modeladmin.admin_site.name,
                        email_server._meta.app_label,
                        email_server._meta.model_name,
                ))
            )
    else:
        form = SetEmailServerPasswordForm(email_server)

    fieldsets = [(None, {'fields': list(form.base_fields)})]
    adminForm = admin.helpers.AdminForm(form, fieldsets, {})

    context = {
        'title': _('Change password: %s') % escape(email_server.name),
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
        'original': email_server,
        'save_as': False,
        'show_save': True,
        **modeladmin.admin_site.each_context(request),
    }

    request.current_app = modeladmin.admin_site.name

    return TemplateResponse(
        request,
        'Notification/change_password.html',
        context,
    )



class EmailServerAdmin(admin.ModelAdmin):
    model = EmailServer
    list_display = ('name', 'is_active', 'email_server', 'email_port','use_tls','server_action')

    fields = ['is_active','name', 'email_server', 'email_port','email_username','email_password','use_tls']

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            if obj.email_username and obj.email_password:
                kwargs['form'] = EmailServerFormEdit
            else:
                kwargs['form'] = EmailServerFormAdd
        else:
            kwargs['form'] = EmailServerFormAdd
        return super().get_form(request, obj, **kwargs)

    def get_fields(self, request, obj=None):
            return ['is_active','name', 'email_server', 'email_port','auth_required','email_username','email_password','use_tls']

    def get_urls(self):
        urls = super(EmailServerAdmin, self).get_urls()
        custom_urls = [
            path(
                '<id>/email_password/',
                self.admin_site.admin_view(self.server_password_change),
                name='server_password_change',
            ),
            url(
                r'^(?P<emailserver_id>.+)/test/$',
                self.admin_site.admin_view(self.test_emailserver),
                name='test-emailserver',
            ),
        ]
        return custom_urls + urls

    @sensitive_post_parameters_m
    def server_password_change(self, request, id, form_url=''):
        return change_password(self, request, id, form_url)

    def server_action(self, obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:test-emailserver', args=[obj.pk]),
            _('Test Connection')
        )
    server_action.short_description = _("Server Actions")

    def test_emailserver(self,request,emailserver_id,*args,**kwargs):
        obj = self.get_object(request,emailserver_id)
        opts = obj._meta

        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,
        )
        obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)

        backend = EmailBackend(
            host=obj.email_server,
            port=obj.email_port,
            username=obj.email_username,
            password=base64.b64decode(obj.email_password).decode('utf-8'),
            use_tls=obj.use_tls,
            fail_silently=False,
            timeout=10
        )

        if obj.auth_required:
            msg = EmailMessage(
                subject=_('ResMan - Test Connection'),
                body= _("If you receive this email the connection was successfully established."),
                from_email=obj.email_username,
                to=[obj.email_username,],
                connection=backend
            )
        else:
            msg = EmailMessage(
                subject=_('ResMan - Test Connection'),
                body=_("If you receive this email the connection was successfully established."),
                from_email="ResMan",
                to=['ernesto@finlay.edu.cu', ],
                connection=backend
            )

        try:
            a = msg.send()

            message = format_html(
                _("Connection to server {} was successfully established."),
                obj_repr
            )
            self.message_user(request, message, messages.SUCCESS)

        except Exception as e:
            message = format_html(
                _("Error in connection, Server {} says: {}"),
                obj_repr,
                str(e)
            )
            self.message_user(request,message,messages.ERROR)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def save_model(self, request, obj, form, change):
        if obj.auth_required:
            if not change:
                obj.email_password = base64.b64encode(obj.email_password.encode('utf-8')).decode()
            else:
                if not form.initial.get('email_password'):
                    obj.email_password = base64.b64encode(obj.email_password.encode('utf-8')).decode()
        else:
            obj.email_username = ""
            obj.email_password = ""
            obj.use_tls = False

        super(EmailServerAdmin,self).save_model(request,obj,form,change)

admin_site.register(EmailServer,EmailServerAdmin)