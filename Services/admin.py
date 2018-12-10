from django.contrib import admin
from django.utils.text import slugify

from .models import Service

class ServiceAdmin(admin.ModelAdmin):
    model = Service
    fields = ('name','description')
    list_display = ('name','description')

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)
        super(ServiceAdmin,self).save_model(request,obj,form,change)

admin.site.register(Service,ServiceAdmin)
