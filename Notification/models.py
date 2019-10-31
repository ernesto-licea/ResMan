from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class EmailServer(models.Model):
    is_active = models.BooleanField(_('is active'), default=True)
    name = models.CharField(_('name'), max_length=100, default="", unique=True)
    email_server = models.CharField(_('email server'), max_length=128, default="")
    email_port = models.PositiveIntegerField(_('email port'), default=25)
    email_username = models.CharField(_('username'),max_length=100,default="")
    email_password = models.CharField(_('password'), max_length=100, default="")
    use_tls = models.BooleanField(_('Use tls?'),default=False)
    creation_date = models.DateTimeField(_("Creation Date"),auto_now_add=True)
    modified_date = models.DateTimeField(_("Modified Date"),auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'email_server'
        verbose_name = _('email server')
        verbose_name_plural = _('email servers')
