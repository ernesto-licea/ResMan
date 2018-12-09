from django.contrib import admin

from .models import Area, Department


class AreaAdmin(admin.ModelAdmin):
    model = Area
    list_display = ('name','responsible','email')

class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    list_display = ('name','responsible','email','area')


admin.site.register(Area,AreaAdmin)
admin.site.register(Department,DepartmentAdmin)
