import base64
import hashlib

from django.conf.urls import url
from django.contrib import admin, messages
from ResMan.admin import admin_site

# Register your models here.
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote, quote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.admin import sensitive_post_parameters_m
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import escape, format_html
from django.utils.http import urlquote
from django.utils.translation import gettext, gettext_lazy as _
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter

from EntStructure.models import Area, Department
from LdapServer.models import LdapServer
from Services.models import Service
from .forms import UserFormEdit, UserFormAdd
from .models import User, UserEnterprise, UserInstitutional, UserGuest, PasswordHistory

def delete_queryset(modeladmin,request,queryset):
    for obj in queryset:
        ldap_error = obj.delete()
        if ldap_error:
            modeladmin.message_user(request, ldap_error, messages.ERROR)
        else:
            if LdapServer.objects.all().count():
                message = _('The {} "{}" was successfully deleted from ldap servers.'.format(
                    modeladmin.model._meta.verbose_name,
                    obj.username
                ))
                modeladmin.message_user(request, message, messages.SUCCESS)


def change_password(modeladmin,request, id, form_url=''):
    if not modeladmin.has_change_permission(request):
        raise PermissionDenied
    user = modeladmin.get_object(request, unquote(id))
    if user is None:
        raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
            'name': modeladmin.model._meta.verbose_name,
            'key': escape(id),
        })
    if request.method == 'POST':
        form = AdminPasswordChangeForm(user, request.POST)
        if form.is_valid():

            password = form.cleaned_data.get('password1')
            user = form.save(commit=False)
            user._password = password

            ldap_error = user.ldap_reset_password(password)
            if ldap_error:
                modeladmin.message_user(request, ldap_error, messages.ERROR)
            else:
                hash_password = make_password(password)
                PasswordHistory.objects.create(user=user, password=hash_password)

                user.password_date = timezone.now()
                user.ftp_md5_password = hashlib.md5(user._password.encode('utf-8')).hexdigest()
                user.session_key = base64.b64encode(user._password.encode('utf-8')).decode()

                user.save()

                change_message = modeladmin.construct_change_message(request, form, None)
                modeladmin.log_change(request, user, change_message)

                msg = gettext('Password changed successfully.')
                messages.success(request, msg)

                update_session_auth_hash(request, form.user)

            return HttpResponseRedirect(
                reverse(
                    '%s:%s_%s_change' % (
                        modeladmin.admin_site.name,
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
        'opts': modeladmin.model._meta,
        'original': user,
        'save_as': False,
        'show_save': True,
        **modeladmin.admin_site.each_context(request),
    }

    request.current_app = modeladmin.admin_site.name

    return TemplateResponse(
        request,
        'admin/auth/user/change_password.html',
        context,
    )

class UserAdmin(PolymorphicParentModelAdmin):
    base_model = User
    child_models = (UserEnterprise, UserInstitutional, UserGuest)
    list_filter = (PolymorphicChildModelFilter,'status')
    list_display = ('username','status','get_full_name','user_type','server_action')
    search_fields = ['username','first_name','last_name']

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
    server_action.short_description = _("Server Actions")

    def sync_data(self,request,user_id,*args,**kwargs):
        obj = self.get_object(request, user_id)
        obj._password = base64.b64decode(obj.session_key.encode('utf-8')).decode()

        ldap_error = obj.ldap_save()

        if ldap_error:
            self.message_user(request, ldap_error, messages.ERROR)
        else:
            self.message_user(request, self._sync_message(obj), messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def delete_queryset(self, request, queryset):
        delete_queryset(self,request,queryset)

    def _sync_message(self,obj):
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
        return message

class UserAdminBase(PolymorphicChildModelAdmin):
    base_model = User
    filter_horizontal = ('services','distribution_list')
    search_fields = ['username','first_name','last_name']
    list_filter = ('status',)


    def get_form(self, request, obj=None, **kwargs):
        if obj:
            kwargs['form'] = UserFormEdit
        else:
            kwargs['form'] = UserFormAdd
        return super().get_form(request, obj, **kwargs)

    def save_related(self, request, form, formsets, change):
        super().save_related(request,form,formsets,change)
        obj = form.save(commit=False)
        if obj.is_staff and not obj.is_superuser:
            ct_user = ContentType.objects.get_for_model(User)
            ct_user_enterprise  = ContentType.objects.get_for_model(UserEnterprise)
            ct_user_institutional = ContentType.objects.get_for_model(UserInstitutional)
            ct_user_guest  = ContentType.objects.get_for_model(UserGuest)
            ct_area = ContentType.objects.get_for_model(Area)
            ct_department  = ContentType.objects.get_for_model(Department)
            ct_services  = ContentType.objects.get_for_model(Service)

            all_permissions = Permission.objects.filter(content_type__in=[
                ct_user,
                ct_user_enterprise,
                ct_user_guest,
                ct_user_institutional,
                ct_area,
                ct_department,
                ct_services
            ])

            for perm in all_permissions:
                obj.user_permissions.add(perm)
            obj.save()

    def _sync_message(self, obj):
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
        return message


    def delete_model(self, request, obj):
        ldap_error = obj.delete()
        if ldap_error:
            self.message_user(request, ldap_error, messages.ERROR)
        else:
            if LdapServer.objects.all().count():
                message = _('The {} "{}" was successfully deleted from ldap servers.'.format(
                    self.model._meta.verbose_name,
                    obj.username
                ))
                self.message_user(request, message, messages.SUCCESS)

    def save_model(self, request, obj, form, change):
        obj.is_active = not obj.status == "inactive"
        if not request.user.is_superuser and change:
            obj.is_superuser = form.initial.get('is_superuser')

        # Create hash password
        if not change:
            obj.ftp_md5_password = hashlib.md5(obj.password.encode('utf-8')).hexdigest()
            obj.session_key = base64.b64encode(obj.password.encode('utf-8')).decode()
            obj.password = make_password(obj.password)


        super(UserAdminBase,self).save_model(request,obj,form,change)

        if not change:
            #Create history del new password
            PasswordHistory.objects.create(user=obj, password=obj.password)

        obj._password = base64.b64decode(obj.session_key.encode('utf-8')).decode()

        obj.distribution_list.clear()
        for d in form.cleaned_data.get('distribution_list'):
            obj.distribution_list.add(d)

        obj.services.clear()
        for s in form.cleaned_data.get('services'):
            obj.services.add(s)

        ldap_error = obj.ldap_save()
        if ldap_error:
            self.message_user(request, ldap_error, messages.ERROR)
        else:

            self.message_user(request, self._sync_message(obj), messages.SUCCESS)

class UserEnterpriseAdmin(UserAdminBase):
    base_model = UserEnterprise
    readonly_fields = ('date_joined','last_login','ftp_md5_password','is_active')
    list_display = ('username','status','get_full_name','user_type','server_action')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('username','first_name','last_name')
        return self.readonly_fields


    def get_fieldsets(self, request, obj=None):
        if not obj:
            fielsets = (
                (None, {
                    'fields': ['date_joined','last_login','status', 'is_staff', 'username', 'password', 'retype_password', 'first_name', 'last_name', 'ci_number', 'services', 'distribution_list']
                }),
                (_('Enterprise Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('enterprise_number', 'area', 'department', 'phone_number', 'extension_number', 'authorized_document'),
                }),
                (_('Email Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('email','email_buzon_size','email_message_size','email_domain'),
                }),
                (_('Internet Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('internet_domain','internet_quota_type','internet_quota_size','internet_extra_quota_size'),
                }),
                (_('FTP Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('ftp_folder','ftp_size'),
                }),
                (_('Additional Description'), {
                    # 'classes': ('collapse',),
                    'fields': ('note',),
                }),
            )
        else:
            fielsets = (
                (None, {
                    'fields': ['date_joined','last_login', 'status', 'is_staff', 'username', 'password', 'first_name', 'last_name', 'ci_number', 'services', 'distribution_list']
                }),
                (_('Enterprise Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('enterprise_number', 'area', 'department', 'phone_number', 'extension_number', 'authorized_document'),
                }),
                (_('Email Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('email', 'email_buzon_size', 'email_message_size', 'email_domain'),
                }),
                (_('Internet Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('internet_domain', 'internet_quota_type', 'internet_quota_size', 'internet_extra_quota_size'),
                }),
                (_('FTP Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('ftp_folder', 'ftp_size'),
                }),
                (_('Additional Description'), {
                    # 'classes': ('collapse',),
                    'fields': ('note',),
                }),
            )
        if request.user.is_superuser:
            fielsets[0][1]['fields'].insert(3,'is_superuser')
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
    server_action.short_description = _("Server Actions")

    def sync_data(self,request,user_id,*args,**kwargs):
        obj = self.get_object(request, user_id)
        obj._password = base64.b64decode(obj.session_key.encode('utf-8')).decode()

        ldap_error = obj.ldap_save()

        if ldap_error:
            self.message_user(request, ldap_error, messages.ERROR)
        else:
            self.message_user(request, self._sync_message(obj), messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def delete_queryset(self, request, queryset):
        delete_queryset(self,request,queryset)

class UserInstitutionalAdmin(UserAdminBase):
    base_model = UserInstitutional
    readonly_fields = ('date_joined','ftp_md5_password','is_active')
    list_display = ('username','status','get_full_name','user_type','server_action')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('username','first_name','last_name')
        return self.readonly_fields

    def get_fieldsets(self, request, obj=None):
        if not obj:
            fieldsets = (
                (None, {
                    'fields': ('date_joined','status', 'username', 'password', 'retype_password', 'first_name', 'last_name', 'services', 'distribution_list')
                }),

                (_('Email Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('email', 'email_buzon_size', 'email_message_size', 'email_domain'),
                }),
                (_('Internet Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('internet_domain', 'internet_quota_type', 'internet_quota_size', 'internet_extra_quota_size'),
                }),
                (_('FTP Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('ftp_folder', 'ftp_size'),
                }),
                (_('Additional Description'), {
                    # 'classes': ('collapse',),
                    'fields': ('note',),
                }),
            )
        else:
            fieldsets = (
                (None, {
                    'fields': ('date_joined','status', 'username', 'password', 'first_name', 'last_name', 'services', 'distribution_list')
                }),

                (_('Email Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('email', 'email_buzon_size', 'email_message_size', 'email_domain'),
                }),
                (_('Internet Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('internet_domain', 'internet_quota_type', 'internet_quota_size', 'internet_extra_quota_size'),
                }),
                (_('FTP Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('ftp_folder', 'ftp_size'),
                }),
                (_('Additional Description'), {
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
    server_action.short_description = _("Server Actions")

    def sync_data(self, request, user_id, *args, **kwargs):
        obj = self.get_object(request, user_id)
        obj._password = base64.b64decode(obj.session_key.encode('utf-8')).decode()

        ldap_error = obj.ldap_save()

        if ldap_error:
            self.message_user(request, ldap_error, messages.ERROR)
        else:
            self.message_user(request, self._sync_message(obj), messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def delete_queryset(self, request, queryset):
        delete_queryset(self,request,queryset)

class UserGuestAdmin(UserAdminBase):
    base_model = UserGuest
    readonly_fields = ('date_joined','ftp_md5_password','is_active')
    list_display = ('username','status','get_full_name','user_type','server_action')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('username','first_name','last_name')
        return self.readonly_fields

    def get_fieldsets(self, request, obj=None):
        if not obj:
            fieldsets = (
                (None, {
                    'fields': ('date_joined','status', 'username', 'password', 'retype_password', 'first_name', 'last_name', 'services', 'distribution_list')
                }),
                (_('Enterprise Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('authorized_document',),
                }),
                (_('Email Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('email', 'email_buzon_size', 'email_message_size', 'email_domain'),
                }),
                (_('Internet Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('internet_domain', 'internet_quota_type', 'internet_quota_size', 'internet_extra_quota_size'),
                }),
                (_('FTP Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('ftp_folder', 'ftp_size'),
                }),
                (_('Additional Description'), {
                    # 'classes': ('collapse',),
                    'fields': ('note',),
                }),
            )
        else:
            fieldsets = (
                (None, {
                    'fields': ('date_joined','status', 'username', 'password', 'first_name', 'last_name', 'services', 'distribution_list')
                }),
                (_('Enterprise Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('authorized_document',),
                }),
                (_('Email Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('email', 'email_buzon_size', 'email_message_size', 'email_domain'),
                }),
                (_('Internet Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('internet_domain', 'internet_quota_type', 'internet_quota_size', 'internet_extra_quota_size'),
                }),
                (_('FTP Service Data'), {
                    # 'classes': ('collapse',),
                    'fields': ('ftp_folder', 'ftp_size'),
                }),
                (_('Additional Description'), {
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
    server_action.short_description = _("Server Actions")

    def sync_data(self, request, user_id, *args, **kwargs):
        obj = self.get_object(request, user_id)
        obj._password = base64.b64decode(obj.session_key.encode('utf-8')).decode()

        ldap_error = obj.ldap_save()

        if ldap_error:
            self.message_user(request, ldap_error, messages.ERROR)
        else:
            self.message_user(request, self._sync_message(obj), messages.SUCCESS)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def delete_queryset(self, request, queryset):
        delete_queryset(self,request,queryset)


admin_site.register(User,UserAdmin)
admin_site.register(UserEnterprise,UserEnterpriseAdmin)
admin_site.register(UserInstitutional,UserInstitutionalAdmin)
admin_site.register(UserGuest,UserGuestAdmin)