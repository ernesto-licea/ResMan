from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.utils import quote
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlquote

from Notification.models import EmailServer
from ResMan.admin import admin_site
from django.utils.translation import gettext_lazy as _


class EmailServerAdmin(admin.ModelAdmin):
    model = EmailServer
    list_display = ('name', 'is_active', 'email_server', 'email_port','use_tls','server_action')

    fields = ['is_active','name', 'email_server', 'email_port','email_username','email_password','use_tls']

    def get_urls(self):
        urls = super(EmailServerAdmin, self).get_urls()
        custom_urls = [
            url(
                r'^(?P<emailserver_id>.+)/test/$',
                self.admin_site.admin_view(self.test_emailserver),
                name='test-emailserver',
            ),
        ]
        return custom_urls + urls

    def server_action(self, obj):
        return format_html(
            '<a class="button" href="{}">{}</a>&nbsp;',
            reverse('admin:test-emailserver', args=[obj.pk]),
            _('Test Connection')
        )
    server_action.short_description = _("Server Actions")

    def test_emailserver(self,request,emailserver_id,*args,**kwargs):
        obj = self.get_object(request,emailserver_id)
        opts = obj._meta


        backend = EmailBackend(
            host=obj.email_server,
            port=obj.email_port,
            username=obj.email_username,
            password=obj.email_password,
            use_tls=obj.use_tls,
            fail_silently=False,
            timeout=10
        )
        try:
            msg = EmailMessage(
                subject=_('Resman - Test Connection'),
                body= _("If you receive this email the connection was successfully established."),
                from_email=obj.email_username,
                to=[obj.email_username,],
                connection=backend
            )
            msg.send()

            obj_url = reverse(
                'admin:%s_%s_change' % (opts.app_label, opts.model_name),
                args=(quote(obj.pk),),
                current_app=self.admin_site.name,
            )
            obj_repr = format_html('<a href="{}">{}</a>', urlquote(obj_url), obj)
            message = format_html(
                _("Connection to server {} was successfully established."),
                obj_repr
            )
            self.message_user(request, message, messages.SUCCESS)
        except Exception as e:
            self.message_user(request,e,messages.ERROR)

        # Return changelist view
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def save_model(self, request, obj, form, change):
        super(EmailServerAdmin,self).save_model(request,obj,form,change)

admin_site.register(EmailServer,EmailServerAdmin)