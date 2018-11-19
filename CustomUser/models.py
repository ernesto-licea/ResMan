import hashlib
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel
from django.utils.translation import gettext_lazy as _

class PasswordHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first = models.CharField(_('first password'),max_length=128,default="",blank=True)
    second = models.CharField(_('second password'),max_length=128,default="",blank=True)
    third = models.CharField(_('third password'),max_length=128,default="",blank=True)
    forth = models.CharField(_('forth password'),max_length=128,default="",blank=True)

    class Meta:
        db_table = 'auth_password_history'
        verbose_name = _('password history')
        verbose_name_plural = _('passwords history')

class CustomUserManager(UserManager,PolymorphicManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('ftp_md5_password',hashlib.md5(password.encode('utf-8')).hexdigest())
        super(CustomUserManager,self).create_user(username,email,password,**extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('ftp_md5_password',hashlib.md5(password.encode('utf-8')).hexdigest())
        super(CustomUserManager,self).create_superuser(username,email,password,**extra_fields)


class User(AbstractUser,PolymorphicModel):

    objects = CustomUserManager()
    STATUS_LIST = [
        (_('active'), _('Active')),
        (_('blocked'), _('Blocked')),
        (_('inactive'), _('Inactive')),
    ]

    EMAIL_DOMAIN_LIST = [
        (_('local'), _('Local')),
        (_('national'), _('National')),
        (_('international'), _('International')),
    ]

    PROXY_DOMAIN_LIST = [
        (_('local'), _('Local')),
        (_('national'), _('National')),
        (_('international'), _('International')),
    ]

    PROXY_QUOTA_LIST = [
        (_('daily'), _('Daily')),
        (_('weekly'), _('Weekly')),
        (_('monthly'), _('Monthly')),
    ]

    status = models.CharField(_('status'),max_length=20, default=STATUS_LIST[0][0])
    password_date = models.DateTimeField(_('password date'),default=timezone.now,blank=True)
    email_buzon_size = models.PositiveIntegerField(_('email buzon size'),default=0,blank=True)
    email_message_size = models.PositiveIntegerField(_('email messages size'),default=0,blank=True)
    email_domain = models.CharField(_('email domain reach'),max_length=20, default=EMAIL_DOMAIN_LIST[0][0],blank=True)
    proxy_quota_type = models.CharField(_('proxy quota type'),max_length=20, default=PROXY_QUOTA_LIST[0][0],blank=True)
    proxy_quota_size = models.PositiveIntegerField(_('proxy quota size'),default=0,blank=True)
    proxy_extra_quota_size = models.PositiveIntegerField(_('proxy extra quota size'),default=0,blank=True)
    proxy_domain = models.CharField(_('proxy domain reach'),max_length=20, default=PROXY_DOMAIN_LIST[0][0],blank=True)
    ftp_folder = models.CharField(_('ftp folder'),max_length=250,default='/home/ftp',blank=True)
    ftp_size = models.PositiveIntegerField(_('ftp size'),default=0,blank=True)
    ftp_md5_password = models.CharField(_('ftp md5 password'),max_length=128,blank=True)


    class Meta(AbstractUser.Meta):
        db_table = 'auth_user'
        swappable = 'AUTH_USER_MODEL'

class UserInstitutional(User):
    notes = models.TextField(default="",blank=True)

    class Meta(User.Meta):
        db_table = 'auth_user_institutional'
        verbose_name = _('institutional user')
        verbose_name_plural = _('institutional users')