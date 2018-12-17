from django.conf.urls import url
from django.contrib import admin
from django.utils.text import slugify

from .models import DistributionList


class DistributionListAdmin(admin.ModelAdmin):
    model = DistributionList
    fields = ('name','responsible','email','description')
    list_display = ('name','responsible','email','description')

    def get_urls(self):
        urls = super(DistributionListAdmin, self).get_urls()
        custom_urls = [
            url(
                r'^(?P<distributionlist_id>.+)/sync/$',
                self.admin_site.admin_view(self.sync_data),
                name='sync-distributionlist',
            ),
        ]
        return custom_urls + urls

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)
        super(DistributionListAdmin,self).save_model(request,obj,form,change)

admin.site.register(DistributionList,DistributionListAdmin)
