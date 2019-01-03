from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.utils import quote
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlquote
from django.utils.translation import gettext_lazy as _

from Services.forms import ServiceForm
from .models import Service


class ServiceAdmin(admin.ModelAdmin):
    model = Service
    form = ServiceForm
    list_display = ('name', 'is_active', 'service_type', 'email','description','server_action')
    list_filter = ('service_type',)

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

    def server_action(self, obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:sync-service', args=[obj.pk]),
            _('sync')
        )

    def sync_data(self,request,service_id,*args,**kwargs):
        service = self.get_object(request,service_id)
        opts = service._meta

        # Construct message to return
        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(service.pk),),
            current_app=self.admin_site.name,
        )
        obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), service)
        message = format_html(
            _("Data from service {} was successfully synchronized with ldap servers."),
            obj_repr
        )
        self.message_user(request, message, messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def save_model(self, request, obj, form, change):
        super(ServiceAdmin,self).save_model(request,obj,form,change)

admin.site.register(Service,ServiceAdmin)
