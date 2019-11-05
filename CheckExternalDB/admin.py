import base64
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote, quote
from django.contrib.auth.admin import sensitive_post_parameters_m
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils.html import format_html, escape
from django.utils.http import urlquote
from django.utils.translation import gettext_lazy as _, gettext
from CheckExternalDB.forms import ExternalDBFormEdit, ExternalDBFormAdd, SetExternalDBPasswordForm
from ResMan.admin import admin_site

from CheckExternalDB.models import ExternalDB

def change_password(modeladmin,request, id, form_url=''):
    if not modeladmin.has_change_permission(request):
        raise PermissionDenied
    db_server = modeladmin.get_object(request, unquote(id))
    if db_server is None:
        raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
            'name': modeladmin.model._meta.verbose_name,
            'key': escape(id),
        })
    if request.method == 'POST':
        form = SetExternalDBPasswordForm(db_server, request.POST)
        if form.is_valid():

            db_password = form.cleaned_data.get('password1')
            db_server = form.save(commit=False)
            db_server.db_password = base64.b64encode(db_password.encode('utf-8')).decode()
            db_server.save()

            change_message = modeladmin.construct_change_message(request, form, None)
            modeladmin.log_change(request, db_server, change_message)

            msg = gettext('Password changed successfully.')
            messages.success(request, msg)

            return HttpResponseRedirect(
                reverse(
                    '%s:%s_%s_changelist' % (
                        modeladmin.admin_site.name,
                        db_server._meta.app_label,
                        db_server._meta.model_name,
                ))
            )
    else:
        form = SetExternalDBPasswordForm(db_server)

    fieldsets = [(None, {'fields': list(form.base_fields)})]
    adminForm = admin.helpers.AdminForm(form, fieldsets, {})

    context = {
        'title': _('Change password: %s') % escape(db_server.name),
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
        'original': db_server,
        'save_as': False,
        'show_save': True,
        **modeladmin.admin_site.each_context(request),
    }

    request.current_app = modeladmin.admin_site.name

    return TemplateResponse(
        request,
        'CheckExternalDB/change_password.html',
        context,
    )


class ExternalDBAdmin(admin.ModelAdmin):
    model = ExternalDB
    list_display = ('name','is_active','db_type','db_host','db_port','user_action','database_action')

    fields = ['is_active','name','db_type','db_host','db_port','db_name','db_username','db_password','db_query','user_field','user_action','notify_informatics_staff','notify_supervisors_staff','email','description']


    def get_form(self, request, obj=None, **kwargs):
        if obj:
            kwargs['form'] = ExternalDBFormEdit
        else:
            kwargs['form'] = ExternalDBFormAdd
        return super().get_form(request, obj, **kwargs)


    def save_model(self, request, obj, form, change):
        if not change:
            obj.db_password = base64.b64encode(obj.db_password.encode('utf-8')).decode()
        super(ExternalDBAdmin,self).save_model(request,obj,form,change)

    def get_urls(self):
        urls = super(ExternalDBAdmin, self).get_urls()
        custom_urls = [
            path(
                '<id>/db_password/',
                self.admin_site.admin_view(self.server_password_change),
                name='server_password_change',
            ),
            url(
                r'^(?P<external_db_id>.+)/check_users/$',
                self.admin_site.admin_view(self.check_users),
                name='check-users',
            ),
            url(
                r'^(?P<external_db_id>.+)/check_connection/$',
                self.admin_site.admin_view(self.check_connection),
                name='check-connection',
            )
        ]
        return custom_urls + urls

    @sensitive_post_parameters_m
    def server_password_change(self, request, id, form_url=''):
        return change_password(self, request, id, form_url)

    def database_action(self, obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:check-users', args=[obj.pk]),
            _('Check Users')
        ) + format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:check-connection', args=[obj.pk]),
            _('Test Connection')
        )
    database_action.short_description = _("Database Action")

    def check_connection(self,request,external_db_id,*args,**kwargs):
        obj = self.get_object(request,external_db_id)
        opts = obj._meta

        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,
        )
        obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)

        status,error = obj.check_connection()
        if status:
            message = format_html(
                _("Connection to server {} was successfully established."),
                obj_repr
            )
        else:
            message = format_html(
                _("Error in connection, Server {} says: {}"),
                obj_repr,
                error
            )
        self.message_user(request, message, messages.SUCCESS if status else messages.ERROR)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def check_users(self,request,external_db_id,*args,**kwargs):
        obj = self.get_object(request,external_db_id)
        opts = obj._meta

        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,
        )
        obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)

        status,user_changed,error = obj.check_users()

        if status:
            if user_changed:
                for user in user_changed:
                    self.message_user(request,user['message'], messages.SUCCESS)
            else:
                message = format_html(
                    _("No user was modified as result of checking agains external database: {}"),
                    obj_repr
                )
                self.message_user(request, message, messages.SUCCESS)
        else:
            message = format_html(
                _("Error in connection, Server {} says: {}"),
                obj_repr,
                error
            )
            self.message_user(request, message, messages.ERROR)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)


admin_site.register(ExternalDB,ExternalDBAdmin)