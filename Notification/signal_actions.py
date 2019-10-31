from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.mail.backends.smtp import EmailBackend
from django.template import Context
from django.template.loader import get_template


def notification_externaldb_check_user(sender,**kwargs):
    changed_users = kwargs['changed_users']
    externaldb = kwargs['externaldb']

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

    backend = EmailBackend(
        host='192.168.1.2',
        port=25,
        username='ernesto@finlay.edu.cu',
        password='Marioneta.pc123',
        use_tls=True
    )

    # Enviar correo
    msg = EmailMultiAlternatives(
        subject="prueba",
        body=text_content,
        from_email='ernesto@finlay.edu.cu',
        to=['ernesto@finlay.edu.cu',],
        connection=backend
    )
    msg.attach_alternative(html_content, "text/html")
    try:
        msg.send()
    except Exception as e:
        print(e)