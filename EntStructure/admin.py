from django.contrib import admin, messages
from django.contrib.admin.utils import quote
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlquote
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _, gettext_lazy

from ResMan.admin import admin_site
from .models import Area, Department


class AreaAdmin(admin.ModelAdmin):
    model = Area
    fields = ('is_active','name','responsible')
    list_display = ('name','is_active','responsible')

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
            _("Data from area {} was successfully synchronized with ldap servers."),
            obj_repr
        )
        return message

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)
        super(AreaAdmin,self).save_model(request,obj,form,change)

        ldap_error = obj.ldap_save()

        if ldap_error:
            self.message_user(request, ldap_error, messages.ERROR)
        else:
            self.message_user(request, self._sync_message(obj), messages.SUCCESS)

class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    fields = ('is_active','name','responsible','area')
    list_display = ('name','is_active','responsible','area')

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)
        super(DepartmentAdmin,self).save_model(request,obj,form,change)


admin_site.register(Area,AreaAdmin)
admin_site.register(Department,DepartmentAdmin)
