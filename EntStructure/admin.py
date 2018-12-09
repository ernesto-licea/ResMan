from django.contrib import admin

from .models import Area, Department


class AreaAdmin(admin.ModelAdmin):
    model = Area
    list_display = ('name','is_active','responsible','email')

    def save_model(self, request, obj, form, change):
        super(AreaAdmin,self).save_model(request,obj,form,change)

class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    list_display = ('name','is_active','responsible','email','area')

    def save_model(self, request, obj, form, change):
        super(DepartmentAdmin,self).save_model(request,obj,form,change)


admin.site.register(Area,AreaAdmin)
admin.site.register(Department,DepartmentAdmin)
