from django.contrib import admin

# Register your models here.
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter

from .models import User, UserEnterprise, UserInstitutional, UserGuest


class UserAdmin(PolymorphicParentModelAdmin):
    base_model = User
    child_models = (UserEnterprise, UserInstitutional, UserGuest)
    list_filter = (PolymorphicChildModelFilter,)

class UserAdminBase(PolymorphicChildModelAdmin):
    base_model = User

class UserEnterpriseAdmin(UserAdminBase):
    base_model = UserEnterprise

    fieldsets = (
        (None, {
            'fields': ('status', 'is_staff', 'username', 'password', 'first_name', 'last_name', 'ci_number')
        }),
        ('Enterprise Data', {
            # 'classes': ('collapse',),
            'fields': ('enterprise_number', 'phone_number', 'extension_number', 'authorized_document'),
        }),
        ('Email Service Data', {
            # 'classes': ('collapse',),
            'fields': ('email','email_buzon_size','email_message_size','email_domain'),
        }),
        ('Internet Service Data', {
            # 'classes': ('collapse',),
            'fields': ('proxy_domain','proxy_quota_type','proxy_quota_size','proxy_extra_quota_size'),
        }),
        ('FTP Service Data', {
            # 'classes': ('collapse',),
            'fields': ('ftp_folder','ftp_size'),
        }),
        ('Additional Description', {
            # 'classes': ('collapse',),
            'fields': ('note',),
        }),
    )


class UserInstitutionalAdmin(UserAdminBase):
    base_model = UserInstitutional

    fieldsets = (
        (None, {
            'fields': ('status', 'username', 'password', 'first_name', 'last_name')
        }),

        ('Email Service Data', {
            # 'classes': ('collapse',),
            'fields': ('email', 'email_buzon_size', 'email_message_size', 'email_domain'),
        }),
        ('Internet Service Data', {
            # 'classes': ('collapse',),
            'fields': ('proxy_domain', 'proxy_quota_type', 'proxy_quota_size', 'proxy_extra_quota_size'),
        }),
        ('FTP Service Data', {
            # 'classes': ('collapse',),
            'fields': ('ftp_folder', 'ftp_size'),
        }),
        ('Additional Description', {
            # 'classes': ('collapse',),
            'fields': ('note',),
        }),
    )

class UserGuestAdmin(UserAdminBase):
    base_model = UserGuest

    fieldsets = (
        (None, {
            'fields': ('status', 'username', 'password', 'first_name', 'last_name')
        }),
        ('Enterprise Data', {
            # 'classes': ('collapse',),
            'fields': ('authorized_document',),
        }),
        ('Email Service Data', {
            # 'classes': ('collapse',),
            'fields': ('email', 'email_buzon_size', 'email_message_size', 'email_domain'),
        }),
        ('Internet Service Data', {
            # 'classes': ('collapse',),
            'fields': ('proxy_domain', 'proxy_quota_type', 'proxy_quota_size', 'proxy_extra_quota_size'),
        }),
        ('FTP Service Data', {
            # 'classes': ('collapse',),
            'fields': ('ftp_folder', 'ftp_size'),
        }),
        ('Additional Description', {
            # 'classes': ('collapse',),
            'fields': ('note',),
        }),
    )

admin.site.register(User,UserAdmin)
admin.site.register(UserEnterprise,UserEnterpriseAdmin)
admin.site.register(UserInstitutional,UserInstitutionalAdmin)
admin.site.register(UserGuest,UserGuestAdmin)