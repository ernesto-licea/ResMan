from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.utils import quote
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlquote
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .models import DistributionList


class DistributionListAdmin(admin.ModelAdmin):
    model = DistributionList
    fields = ('name','responsible','email','description')
    list_display = ('name','responsible','email','description','server_action')

    def server_action(self, obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:sync-distributionlist', args=[obj.pk]),
            _('ldap sync')
        )

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

    def sync_data(self,request,distributionlist_id,*args,**kwargs):
        obj = self.get_object(request,distributionlist_id)
        opts = obj._meta

        # Construct message to return
        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,
        )
        obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)
        message = format_html(
            _("Data from Distribution List {} was successfully sent to ldap servers."),
            obj_repr
        )
        self.message_user(request, message, messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def save_model(self, request, obj, form, change):
        obj.slugname = slugify(obj.name)

        if not change:
            ldap_error = obj.create_ldap_distribution_list()
        else:
            ldap_error = obj.modify_ldap_distribution_list()

        if ldap_error:
            self.message_user(request,'error', messages.ERROR)
        else:
            self.message_user(request,'success',messages.SUCCESS)

        super(DistributionListAdmin,self).save_model(request,obj,form,change)

admin.site.register(DistributionList,DistributionListAdmin)
