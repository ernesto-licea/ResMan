import base64

from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import get_template
from django.apps import apps
from django.utils.translation import gettext_lazy as _


def notification_externaldb_check_user(sender,**kwargs):
    changed_users = kwargs['changed_users']
    externaldb = kwargs['externaldb']
    if externaldb.email or externaldb.notify_informatics_staff or externaldb.notify_supervisors_staff:
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

        email_users = []
        appconfig = apps.get_app_config('CustomUser')
        User = appconfig.get_model('User','User')

        if externaldb.notify_informatics_staff:
            staff_users = User.objects.filter(is_active=True, is_staff=True)
            for user in staff_users:
                if user.email and user.email not in email_users:
                    email_users.append(user.email)

        if externaldb.notify_supervisors_staff:
            supervisor_users = User.objects.filter(is_active=True,is_supervisor=True)
            for user in supervisor_users:
                if user.email and user.email not in email_users:
                    email_users.append(user.email)

        if externaldb.email and externaldb.email not in email_users:
            email_users.append(externaldb.email)

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
                to=email_users,
                connection=backend
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()


def notification_password_changed_successfully(sender,**kwargs):
    user = kwargs['obj']
    language_code = kwargs['language_code']
    if user.email:
        html_content = get_template(
            "Notification/password_changed_successfully.html").render(
            {
                "user": user,
            })

        # Crear correo text
        text_content = get_template(
            "Notification/password_changed_successfully.txt").render({
            "user": user,
        })


        appconfig = apps.get_app_config('Notification')
        EmailServer = appconfig.get_model('EmailServer', 'EmailServer')
        email_server_list = EmailServer.objects.filter(is_active=True)


        appconfig = apps.get_app_config('Help')
        Help = appconfig.get_model('Help','Help')
        help_text = Help.objects.get(id=4)

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
                subject=_("ResMan - Password successfully changed"),
                body=text_content,
                from_email=mail_from,
                to=[user.email,],
                connection=backend
            )
            msg.attach_alternative(html_content, "text/html")

            if language_code.find("es") != -1:
                if help_text.attachment_es:
                    msg.attach("%s.pdf" % help_text.name_es, help_text.attachment_es.read(), "application/pdf")
            else:
                if help_text.attachment_en:
                    msg.attach("%s.pdf" %help_text.name_en,help_text.attachment_en.read(),"application/pdf")
            msg.send()