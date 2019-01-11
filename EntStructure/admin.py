from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.utils import quote
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlquote
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .models import Area, Department


class AreaAdmin(admin.ModelAdmin):
    model = Area
    fields = ('is_active','name','responsible')
    list_display = ('name','is_active','responsible','server_action')

    def server_action(self, obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:sync-area', args=[obj.pk]),
            _('ldap sync')
        )

    def get_urls(self):
        urls = super(AreaAdmin, self).get_urls()
        custom_urls = [
            url(
                r'^(?P<area_id>.+)/sync/$',
                self.admin_site.admin_view(self.sync_data),
                name='sync-area',
            ),
        ]
        return custom_urls + urls

    def sync_data(self,request,area_id,*args,**kwargs):
        obj = self.get_object(request,area_id)
        opts = obj._meta

        # Construct message to return
        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,
        )
        obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)
        message = format_html(
            _("Data from area {} was successfully sent to ldap servers."),
            obj_repr
        )
        self.message_user(request, message, messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)
        super(AreaAdmin,self).save_model(request,obj,form,change)

class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    fields = ('is_active','name','responsible','area')
    list_display = ('name','is_active','responsible','area','server_action')

    def server_action(self, obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:sync-department', args=[obj.pk]),
            _('ldap sync')
        )

    def get_urls(self):
        urls = super(DepartmentAdmin, self).get_urls()
        custom_urls = [
            url(
                r'^(?P<department_id>.+)/sync/$',
                self.admin_site.admin_view(self.sync_data),
                name='sync-department',
            ),
        ]
        return custom_urls + urls

    def sync_data(self,request,department_id,*args,**kwargs):
        obj = self.get_object(request,department_id)
        opts = obj._meta

        # Construct message to return
        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,
        )
        obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)
        message = format_html(
            _("Data from department {} was successfully sent to ldap servers."),
            obj_repr
        )
        self.message_user(request, message, messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)
        super(DepartmentAdmin,self).save_model(request,obj,form,change)


admin.site.register(Area,AreaAdmin)
admin.site.register(Department,DepartmentAdmin)
