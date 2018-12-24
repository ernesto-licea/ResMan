from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class LdapServer(models.Model):
    is_active = models.BooleanField(_('is active'), default=True)
    name = models.CharField(_('name'), max_length=100, default="", unique=True)
    domain = models.CharField(_('domain'), max_length=100, default="")
    search_base = models.CharField(_('search base'),max_length=100,default="")
    server_host = models.CharField(_('server host'), max_length=50, default="", unique=True)
    server_port = models.PositiveIntegerField(_('server port'), default=389)
    start_tls = models.BooleanField(_('start tls'),default=False)
    admin_username = models.CharField(_('admin username'), max_length=100, default="")
    admin_password = models.CharField(_('admin password'), max_length=50, default="")

    email_domain = models.CharField(_('email domain map'), max_length=50, default="physicalDeliveryOfficeName")
    email_buzon_size = models.CharField(_('email buzon size map'), max_length=50, default="otherMailbox")
    email_message_size = models.CharField(_('email message size map'), max_length=50, default="postalCode")

    internet_domain = models.CharField(_('internet domain map'), max_length=50, default="employeeType")
    internet_quota_type = models.CharField(_('internet quota type map'), max_length=50, default="division")
    internet_quota_size = models.CharField(_('internet quota size map'), max_length=50, default="employeeNumber")
    internet_extra_quota_size = models.CharField(_('internet extra quota size map'), max_length=50, default="telexNumber")

    ftp_home = models.CharField(_('ftp home'), max_length=50, default="homeDrive")
    ftp_size = models.CharField(_('ftp size'), max_length=50, default="uidNumber")

    def socket(self):
        return "{}:{}".format(self.server_host,self.server_port)
    socket.short_description = _('Server Connection')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'ldap_server'
        verbose_name = _('active directory server')
        verbose_name_plural = _('active directory servers')
