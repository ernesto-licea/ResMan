from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.utils import quote
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlquote
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _, gettext_lazy

from ResMan.admin_actions import delete_selected_services
from Services.forms import ServiceForm
from .models import Service


class ServiceAdmin(admin.ModelAdmin):
    model = Service
    form = ServiceForm
    list_display = ('name', 'is_active', 'service_type', 'email','description','server_action')
    list_filter = ('service_type',)
    actions = ['delete_selected',]

    fields = ['is_active','name', 'service_type', 'email','description']

    def get_urls(self):
        urls = super(ServiceAdmin, self).get_urls()
        custom_urls = [
            url(
                r'^(?P<service_id>.+)/sync/$',
                self.admin_site.admin_view(self.sync_data),
                name='sync-service',
            ),
        ]
        return custom_urls + urls

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.name in ['Internet','Email','Chat','Ftp']:
                return False
        return True

    def has_change_permission(self, request, obj=None):
        if obj:
            if obj.name in ['Internet','Email','Chat','Ftp']:
                return False
        return True

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('name',)
        return self.readonly_fields

    def server_action(self, obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:sync-service', args=[obj.pk]),
            _('sync')
        )
    server_action.short_description = _("Server Actions")

    def sync_data(self,request,service_id,*args,**kwargs):
        obj = self.get_object(request,service_id)

        ldap_error = obj.ldap_save()

        if ldap_error:
            self.message_user(request, ldap_error, messages.ERROR)
        else:
            self.message_user(request, self._sync_message(obj), messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)

        super(ServiceAdmin,self).save_model(request,obj,form,change)

        ldap_error = obj.ldap_save()

        if ldap_error:
            self.message_user(request, ldap_error, messages.ERROR)
        else:
            self.message_user(request, self._sync_message(obj), messages.SUCCESS)

    def delete_model(self, request, obj):
        ldap_error = obj.delete()
        if ldap_error:
            self.message_user(request, ldap_error, messages.ERROR)
        else:
            message = _('The service "{}" was successfully deleted from ldap servers.'.format(obj.name))
            self.message_user(request, message, messages.SUCCESS)

    def response_delete(self, request, obj_display, obj_id):
        response = super().response_delete(request,obj_display,obj_id)
        if self.get_object(request,obj_id):
            storage = messages.get_messages(request)
            for a in storage:
                pass
        return response

    def delete_selected(self,request,queryset):
        return delete_selected_services(self,request,queryset)

    delete_selected.allowed_permissions = ('delete',)
    delete_selected.short_description = gettext_lazy("Delete selected %(verbose_name_plural)s")

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
            _("Data from service {} was successfully synchronized with ldap servers."),
            obj_repr
        )
        return message

admin.site.register(Service,ServiceAdmin)
