from django.contrib import admin
from django.utils.text import slugify

from .models import Service

class ServiceAdmin(admin.ModelAdmin):
    model = Service
    fields = ('name','description')
    list_display = ('name','description')
    builtin_services = ['internet','email','ftp','chat']

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)
        super(ServiceAdmin,self).save_model(request,obj,form,change)

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.name in self.builtin_services:
                return False
        return True

    def has_change_permission(self, request, obj=None):
        if obj:
            if obj.name in self.builtin_services:
                return False
        return True

admin.site.register(Service,ServiceAdmin)
