from django.contrib import admin

from .models import LdapServer


class LdapServerAdmin(admin.ModelAdmin):
    model = LdapServer
    fields = "__all__"
    list_display = ('name','is_active','socket','bind_dn')

    def save_model(self, request, obj, form, change):
        super(LdapServerAdmin,self).save_model(request,obj,form,change)

admin.site.register(LdapServer,LdapServerAdmin)