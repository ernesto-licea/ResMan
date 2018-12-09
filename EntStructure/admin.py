from django.contrib import admin
from django.utils.text import slugify

from .models import Area, Department


class AreaAdmin(admin.ModelAdmin):
    model = Area
    fields = ('is_active','name','responsible','email')
    list_display = ('name','is_active','responsible','email')

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)
        super(AreaAdmin,self).save_model(request,obj,form,change)

class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    fields = ('is_active','name','responsible','email','area')
    list_display = ('name','is_active','responsible','email','area')

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)
        super(DepartmentAdmin,self).save_model(request,obj,form,change)


admin.site.register(Area,AreaAdmin)
admin.site.register(Department,DepartmentAdmin)
