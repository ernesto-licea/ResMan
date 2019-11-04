import base64

from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import get_template
from django.apps import apps
from django.utils.translation import gettext_lazy as _


def notification_externaldb_check_user(sender,**kwargs):
    changed_users = kwargs['changed_users']
    externaldb = kwargs['externaldb']
    if externaldb.email:
        html_content = get_template(
            "Notification/externaldb_check_users.html").render(
            {
                "changed_users":changed_users,
                "externaldb": externaldb
            })

        # Crear correo text
        text_content = get_template(
            "Notification/externaldb_check_users.txt").render({
            "changed_users": changed_users,
            "externaldb": externaldb
        })

        appconfig = apps.get_app_config('Notification')
        EmailServer = appconfig.get_model('EmailServer', 'EmailServer')
        email_server_list = EmailServer.objects.filter(is_active=True)

        for server in email_server_list:

            if server.auth_required:
                backend = EmailBackend(
                    host=server.email_server,
                    port=server.email_port,
                    username=server.email_username,
                    password=base64.b64decode(server.email_password).decode('utf-8'),
                    use_tls=server.use_tls,
                    fail_silently=True,
                    timeout=10
                )
                mail_from = server.email_username
            else:
                backend = EmailBackend(
                    host=server.email_server,
                    port=server.email_port,
                    username="",
                    password="",
                    use_tls=False,
                    fail_silently=True,
                    timeout=10
                )
                mail_from = "ResMan"

            # Enviar correo
            msg = EmailMultiAlternatives(
                subject=_("ResMan - Result of the user check against external database '%(database)s'") %{'database':externaldb.name},
                body=text_content,
                from_email=mail_from,
                to=[externaldb.email,],
                connection=backend
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
