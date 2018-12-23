import hashlib

from django.conf.urls import url
from django.contrib import admin, messages

# Register your models here.
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote, quote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.admin import sensitive_post_parameters_m
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import escape, format_html
from django.utils.http import urlquote
from django.utils.translation import gettext, gettext_lazy as _
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter

from .forms import UserFormEdit, UserFormAdd
from .models import User, UserEnterprise, UserInstitutional, UserGuest, PasswordHistory


def change_password(self,request, id, form_url=''):
    if not self.has_change_permission(request):
        raise PermissionDenied
    user = self.get_object(request, unquote(id))
    if user is None:
        raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
            'name': self.model._meta.verbose_name,
            'key': escape(id),
        })
    if request.method == 'POST':
        form = AdminPasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password_date = timezone.now()
            user.ftp_md5_password = hashlib.md5(user._password.encode('utf-8')).hexdigest()
            user.save()

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
        form = AdminPasswordChangeForm(user)

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
        'admin/auth/user/change_password.html',
        context,
    )

class UserAdmin(PolymorphicParentModelAdmin):
    base_model = User
    child_models = (UserEnterprise, UserInstitutional, UserGuest)
    list_filter = (PolymorphicChildModelFilter,)
    list_display = ('username','status','get_full_name','user_type','server_action')

    def get_urls(self):
        return [
            path(
                '<id>/password/',
                self.admin_site.admin_view(self.user_password_change),
                name='user_password_change',
            ),
            url(
               r'^(?P<user_id>.+)/sync/$',
               self.admin_site.admin_view(self.sync_data),
               name='sync-user',
            ),
        ] + super().get_urls()

    @sensitive_post_parameters_m
    def user_password_change(self, request, id, form_url=''):
        return change_password(self,request,id,form_url)

    def server_action(self,obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:user_password_change', args=[obj.pk]),
            _('Reset Password')
        ) + format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:sync-user', args=[obj.pk]),
            _('Ldap Sync')
        )

    def sync_data(self,request,user_id,*args,**kwargs):
        obj = self.get_object(request, user_id)
        opts = obj._meta

        # Construct message to return
        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,
        )
        obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)
        message = format_html(
            _("Data from user {} was successfully synchronized with ldap servers."),
            obj_repr
        )
        self.message_user(request, message, messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

class UserAdminBase(PolymorphicChildModelAdmin):
    base_model = User
    filter_horizontal = ('services','distribution_list')


    def get_form(self, request, obj=None, **kwargs):
        if obj:
            kwargs['form'] = UserFormEdit
        else:
            kwargs['form'] = UserFormAdd
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.is_active = obj.status == "active"

        # Create hash password
        if not change:
            obj.ftp_md5_password = hashlib.md5(obj.password.encode('utf-8')).hexdigest()
            obj.password = make_password(obj.password)

        super(UserAdminBase,self).save_model(request,obj,form,change)

        # Create history del new password
        PasswordHistory.objects.create(user=obj, password=obj.password)

class UserEnterpriseAdmin(UserAdminBase):
    base_model = UserEnterprise
    readonly_fields = ('date_joined','last_login','ftp_md5_password','is_active')
    list_display = ('username','status','get_full_name','user_type','server_action')


    def get_fieldsets(self, request, obj=None):
        if not obj:
            fielsets = (
                (None, {
                    'fields': ('date_joined','last_login','status', 'is_staff', 'username', 'password', 'retype_password', 'first_name', 'last_name', 'ci_number', 'services', 'distribution_list')
                }),
                ('Enterprise Data', {
                    # 'classes': ('collapse',),
                    'fields': ('enterprise_number', 'area', 'department', 'phone_number', 'extension_number', 'authorized_document'),
                }),
                ('Email Service Data', {
                    # 'classes': ('collapse',),
                    'fields': ('email','email_buzon_size','email_message_size','email_domain'),
                }),
                ('Internet Service Data', {
                    # 'classes': ('collapse',),
                    'fields': ('internet_domain','internet_quota_type','internet_quota_size','internet_extra_quota_size'),
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
                    'fields': ('date_joined','last_login', 'status', 'is_staff', 'username', 'password', 'first_name', 'last_name', 'ci_number', 'services', 'distribution_list')
                }),
                ('Enterprise Data', {
                    # 'classes': ('collapse',),
                    'fields': ('enterprise_number', 'area', 'department', 'phone_number', 'extension_number', 'authorized_document'),
                }),
                ('Email Service Data', {
                    # 'classes': ('collapse',),
                    'fields': ('email', 'email_buzon_size', 'email_message_size', 'email_domain'),
                }),
                ('Internet Service Data', {
                    # 'classes': ('collapse',),
                    'fields': ('internet_domain', 'internet_quota_type', 'internet_quota_size', 'internet_extra_quota_size'),
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

    def get_urls(self):
        return [
            path(
                '<id>/password/',
                self.admin_site.admin_view(self.user_enterprise_password_change),
                name='user_enterprise_password_change',
            ),
            url(
               r'^(?P<user_id>.+)/sync/$',
               self.admin_site.admin_view(self.sync_data),
               name='sync-user-enterprise',
            ),
        ] + super().get_urls()

    @sensitive_post_parameters_m
    def user_enterprise_password_change(self, request, id, form_url=''):
        return change_password(self, request, id, form_url)

    def server_action(self,obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:user_enterprise_password_change', args=[obj.pk]),
            _('Reset Password')
        ) + format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:sync-user-enterprise', args=[obj.pk]),
            _('Ldap Sync')
        )

    def sync_data(self,request,user_id,*args,**kwargs):
        obj = self.get_object(request, user_id)
        opts = obj._meta

        # Construct message to return
        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,
        )
        obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)
        message = format_html(
            _("Data from user {} was successfully synchronized with ldap servers."),
            obj_repr
        )
        self.message_user(request, message, messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

class UserInstitutionalAdmin(UserAdminBase):
    base_model = UserInstitutional
    readonly_fields = ('date_joined','ftp_md5_password','is_active')
    list_display = ('username','status','get_full_name','user_type','server_action')

    def get_fieldsets(self, request, obj=None):
        if not obj:
            fieldsets = (
                (None, {
                    'fields': ('date_joined','status', 'username', 'password', 'retype_password', 'first_name', 'last_name', 'services', 'distribution_list')
                }),

                ('Email Service Data', {
                    # 'classes': ('collapse',),
                    'fields': ('email', 'email_buzon_size', 'email_message_size', 'email_domain'),
                }),
                ('Internet Service Data', {
                    # 'classes': ('collapse',),
                    'fields': ('internet_domain', 'internet_quota_type', 'internet_quota_size', 'internet_extra_quota_size'),
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
                    'fields': ('date_joined','status', 'username', 'password', 'first_name', 'last_name', 'services', 'distribution_list')
                }),

                ('Email Service Data', {
                    # 'classes': ('collapse',),
                    'fields': ('email', 'email_buzon_size', 'email_message_size', 'email_domain'),
                }),
                ('Internet Service Data', {
                    # 'classes': ('collapse',),
                    'fields': ('internet_domain', 'internet_quota_type', 'internet_quota_size', 'internet_extra_quota_size'),
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

    def get_urls(self):
        return [
            path(
                '<id>/password/',
                self.admin_site.admin_view(self.user_institutional_password_change),
                name='user_institutional_password_change',
            ),
            url(
               r'^(?P<user_id>.+)/sync/$',
               self.admin_site.admin_view(self.sync_data),
               name='sync-user-institutional',
            ),
        ] + super().get_urls()

    @sensitive_post_parameters_m
    def user_institutional_password_change(self, request, id, form_url=''):
        return change_password(self, request, id, form_url)

    def server_action(self,obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:user_institutional_password_change', args=[obj.pk]),
            _('Reset Password')
        ) + format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:sync-user-institutional', args=[obj.pk]),
            _('Ldap Sync')
        )

    def sync_data(self,request,user_id,*args,**kwargs):
        obj = self.get_object(request, user_id)
        opts = obj._meta

        # Construct message to return
        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,
        )
        obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)
        message = format_html(
            _("Data from user {} was successfully synchronized with ldap servers."),
            obj_repr
        )
        self.message_user(request, message, messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

class UserGuestAdmin(UserAdminBase):
    base_model = UserGuest
    readonly_fields = ('date_joined','ftp_md5_password','is_active')
    list_display = ('username','status','get_full_name','user_type','server_action')

    def get_fieldsets(self, request, obj=None):
        if not obj:
            fieldsets = (
                (None, {
                    'fields': ('date_joined','status', 'username', 'password', 'retype_password', 'first_name', 'last_name', 'services', 'distribution_list')
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
                    'fields': ('internet_domain', 'internet_quota_type', 'internet_quota_size', 'internet_extra_quota_size'),
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
                    'fields': ('date_joined','status', 'username', 'password', 'first_name', 'last_name', 'services', 'distribution_list')
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
                    'fields': ('internet_domain', 'internet_quota_type', 'internet_quota_size', 'internet_extra_quota_size'),
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

    def get_urls(self):
        return [
            path(
                '<id>/password/',
                self.admin_site.admin_view(self.user_guest_password_change),
                name='user_guest_password_change',
            ),
            url(
               r'^(?P<user_id>.+)/sync/$',
               self.admin_site.admin_view(self.sync_data),
               name='sync-user-guest',
            ),
        ] + super().get_urls()

    @sensitive_post_parameters_m
    def user_guest_password_change(self, request, id, form_url=''):
        return change_password(self, request, id, form_url)

    def server_action(self,obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:user_guest_password_change', args=[obj.pk]),
            _('Reset Password')
        ) + format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:sync-user-guest', args=[obj.pk]),
            _('Ldap Sync')
        )

    def sync_data(self,request,user_id,*args,**kwargs):
        obj = self.get_object(request, user_id)
        opts = obj._meta

        # Construct message to return
        obj_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,
        )
        obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)
        message = format_html(
            _("Data from user {} was successfully synchronized with ldap servers."),
            obj_repr
        )
        self.message_user(request, message, messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)


admin.site.register(User,UserAdmin)
admin.site.register(UserEnterprise,UserEnterpriseAdmin)
admin.site.register(UserInstitutional,UserInstitutionalAdmin)
admin.site.register(UserGuest,UserGuestAdmin)