from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class LdapServer(models.Model):
    is_active = models.BooleanField(_('is active'), default=True)
    name = models.CharField(_('name'), max_length=100, default="", unique=True)
    server_host = models.CharField(_('server host'), max_length=50, default="", unique=True)
    server_port = models.PositiveIntegerField(_('server port'), default=389)
    start_tls = models.BooleanField(_('start tls'),default=False)
    bind_dn = models.CharField(_('bind DN'), max_length=100, default="")
    bind_password = models.CharField(_('bind password'), max_length=50, default="")

    email_domain = models.CharField(_('email domain map'), max_length=50, default="")
    email_buzon_size = models.CharField(_('email buzon size map'), max_length=50, default="")
    email_message_size = models.CharField(_('email message size map'), max_length=50, default="")

    proxy_domain = models.CharField(_('proxy domain map'), max_length=50, default="")
    proxy_quota_type = models.CharField(_('proxy quota type map'), max_length=50, default="")
    proxy_quota_size = models.CharField(_('proxy quota size map'), max_length=50, default="")
    proxy_extra_quota_size = models.CharField(_('proxy extra quota size map'), max_length=50, default="")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'ldap_server'
        verbose_name = _('ldap server')
        verbose_name_plural = _('ldap servers')
