from django.contrib import admin
from django.utils.text import slugify

from ResMan.admin import admin_site
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


admin_site.register(Area,AreaAdmin)
admin_site.register(Department,DepartmentAdmin)
