import base64

import MySQLdb
import pymssql
from django.conf.urls import url
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from CheckExternalDB.forms import ExternalDBFormEdit, ExternalDBFormAdd
from CustomUser.models import UserEnterprise
from ResMan.admin import admin_site

from CheckExternalDB.models import ExternalDB


class ExternalDBAdmin(admin.ModelAdmin):
    model = ExternalDB
    # form = ServiceForm
    list_display = ('name','is_active','db_type','db_host','db_port','user_action','database_action')
    list_filter = ('is_active',)

    fields = ['is_active','name','db_type','db_host','db_port','db_name','db_username','db_password','db_query','user_field','user_action','email','description']


    def get_form(self, request, obj=None, **kwargs):
        if obj:
            kwargs['form'] = ExternalDBFormEdit
        else:
            kwargs['form'] = ExternalDBFormAdd
        return super().get_form(request, obj, **kwargs)


    def save_model(self, request, obj, form, change):
        if not change:
            obj.db_password = base64.b64encode(obj.db_password.encode('utf-8'))
        super(ExternalDBAdmin,self).save_model(request,obj,form,change)

    def get_urls(self):
        urls = super(ExternalDBAdmin, self).get_urls()
        custom_urls = [
            url(
                r'^(?P<external_db_id>.+)/check/$',
                self.admin_site.admin_view(self.check_users),
                name='check-users',
            )
        ]
        return custom_urls + urls

    def database_action(self, obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:check-users', args=[obj.pk]),
            _('Check Users')
        )
    database_action.short_description = _("Database Action")


    def check_users(self,request,external_db_id,*args,**kwargs):
        obj = self.get_object(request,external_db_id)

        user_changed = obj.check_users()

        for user in user_changed:
            self.message_user(request,user['message'], messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)


admin_site.register(ExternalDB,ExternalDBAdmin)