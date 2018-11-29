import hashlib

from django.contrib import admin

# Register your models here.
from django.contrib.auth.hashers import make_password
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter

from .forms import UserFormEdit, UserFormAdd
from .models import User, UserEnterprise, UserInstitutional, UserGuest


class UserAdmin(PolymorphicParentModelAdmin):
    base_model = User
    child_models = (UserEnterprise, UserInstitutional, UserGuest)
    list_filter = (PolymorphicChildModelFilter,)

class UserAdminBase(PolymorphicChildModelAdmin):
    base_model = User

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            kwargs['form'] = UserFormEdit
        else:
            kwargs['form'] = UserFormAdd
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        # If user is staff then is superuser too
        if obj.is_staff:
            obj.is_superuser = True

        # Create hash password
        if not change:
            obj.ftp_md5_password = hashlib.md5(obj.password.encode('utf-8')).hexdigest()
            obj.password = make_password(obj.password)

        super(UserAdminBase,self).save_model(request,obj,form,change)

class UserEnterpriseAdmin(UserAdminBase):
    base_model = UserEnterprise


    def get_fieldsets(self, request, obj=None):
        if not obj:
            fielsets = (
                (None, {
                    'fields': ('status', 'is_staff', 'username', 'password', 'retype_password', 'first_name', 'last_name', 'ci_number')
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
        else:
            fielsets = (
                (None, {
                    'fields': (
                    'status', 'is_staff', 'username', 'password', 'first_name', 'last_name',
                    'ci_number')
                }),
                ('Enterprise Data', {
                    # 'classes': ('collapse',),
                    'fields': ('enterprise_number', 'phone_number', 'extension_number', 'authorized_document'),
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
        return fielsets

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('password',)
        return self.readonly_fields

class UserInstitutionalAdmin(UserAdminBase):
    base_model = UserInstitutional

    fieldsets = (
        (None, {
            'fields': ('status', 'username', 'password', 'retype_password', 'first_name', 'last_name')
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
            'fields': ('status', 'username', 'password', 'retype_password', 'first_name', 'last_name')
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