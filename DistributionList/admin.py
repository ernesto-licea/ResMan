from django.contrib import admin
from django.utils.text import slugify

from .models import DistributionList


class DistributionListAdmin(admin.ModelAdmin):
    model = DistributionList
    fields = ('name','responsible','email','description')
    list_display = ('name','responsible','email','description')

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)
        super(DistributionListAdmin,self).save_model(request,obj,form,change)

admin.site.register(DistributionList,DistributionListAdmin)
