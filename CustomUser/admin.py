import hashlib

from django.contrib import admin, messages

# Register your models here.
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.admin import sensitive_post_parameters_m
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import escape
from django.utils.translation import gettext, gettext_lazy as _
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter

from .forms import UserFormEdit, UserFormAdd
from .models import User, UserEnterprise, UserInstitutional, UserGuest


class UserAdminMixin(admin.ModelAdmin):
    change_password_form = AdminPasswordChangeForm
    change_user_password_template = None

    def get_urls(self):
        return [
            path(
                '<id>/password/',
                self.admin_site.admin_view(self.user_change_password),
                name='auth_user_password_change',
            ),
        ] + super().get_urls()

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = self.get_object(request, unquote(id))
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(id),
            })
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = gettext('Password changed successfully.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        '%s:%s_%s_change' % (
                            self.admin_site.name,
                            user._meta.app_label,
                            user._meta.model_name,
                        ),
                        args=(user.pk,),
                    )
                )
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context,
        )

class UserAdmin(PolymorphicParentModelAdmin,UserAdminMixin):
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

class UserEnterpriseAdmin(UserAdminBase,UserAdminMixin):
    base_model = UserEnterprise
    readonly_fields = ('date_joined','last_login')


    def get_fieldsets(self, request, obj=None):
        if not obj:
            fielsets = (
                (None, {
                    'fields': ('date_joined','last_login','status', 'is_staff', 'username', 'password', 'retype_password', 'first_name', 'last_name', 'ci_number')
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
                    'fields': ('date_joined','last_login', 'status', 'is_staff', 'username', 'password', 'first_name', 'last_name', 'ci_number')
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

class UserInstitutionalAdmin(UserAdminBase,UserAdminMixin):
    base_model = UserInstitutional
    readonly_fields = ('date_joined',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            fieldsets = (
                (None, {
                    'fields': ('date_joined','status', 'username', 'password', 'retype_password', 'first_name', 'last_name')
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
        else:
            fieldsets = (
                (None, {
                    'fields': ('date_joined','status', 'username', 'password', 'first_name', 'last_name')
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
        return  fieldsets

class UserGuestAdmin(UserAdminBase,UserAdminMixin):
    base_model = UserGuest
    readonly_fields = ('date_joined',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            fieldsets = (
                (None, {
                    'fields': ('date_joined','status', 'username', 'password', 'retype_password', 'first_name', 'last_name')
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
        else:
            fieldsets = (
                (None, {
                    'fields': ('date_joined','status', 'username', 'password', 'first_name', 'last_name')
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
        return fieldsets

admin.site.register(User,UserAdmin)
admin.site.register(UserEnterprise,UserEnterpriseAdmin)
admin.site.register(UserInstitutional,UserInstitutionalAdmin)
admin.site.register(UserGuest,UserGuestAdmin)