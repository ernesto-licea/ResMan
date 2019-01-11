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
    list_display = ('name','is_active','responsible')

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)
        super(AreaAdmin,self).save_model(request,obj,form,change)

class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    fields = ('is_active','name','responsible','area')
    list_display = ('name','is_active','responsible','area')

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)
        super(DepartmentAdmin,self).save_model(request,obj,form,change)


admin.site.register(Area,AreaAdmin)
admin.site.register(Department,DepartmentAdmin)
