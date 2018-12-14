import hashlib
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel
from django.utils.translation import gettext_lazy as _

from EntStructure.models import Area,Department


class PasswordHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    password = models.CharField(_('password'),max_length=150,default="")
    date_password = models.DateTimeField(_("date password"),default=timezone.now)

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
    is_staff = models.BooleanField(
        _('Informatics Staff'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    status = models.CharField(_('status'),max_length=20, choices=STATUS_LIST, default=STATUS_LIST[0][0])
    password_date = models.DateTimeField(_('password date'),default=timezone.now,blank=True)
    email_buzon_size = models.PositiveIntegerField(_('email buzon size'),default=0,blank=True)
    email_message_size = models.PositiveIntegerField(_('email messages size'),default=0,blank=True)
    email_domain = models.CharField(_('email domain reach'),max_length=20, choices=EMAIL_DOMAIN_LIST ,default=EMAIL_DOMAIN_LIST[0][0],blank=True)
    proxy_quota_type = models.CharField(_('proxy quota type'),max_length=20, choices=PROXY_QUOTA_LIST ,default=PROXY_QUOTA_LIST[0][0],blank=True)
    proxy_quota_size = models.PositiveIntegerField(_('proxy quota size'),default=0,blank=True)
    proxy_extra_quota_size = models.PositiveIntegerField(_('proxy extra quota size'),default=0,blank=True)
    proxy_domain = models.CharField(_('proxy domain reach'),max_length=20, choices=PROXY_DOMAIN_LIST, default=PROXY_DOMAIN_LIST[0][0],blank=True)
    ftp_folder = models.CharField(_('ftp folder'),max_length=250,default='/home/ftp',blank=True)
    ftp_size = models.PositiveIntegerField(_('ftp size'),default=0,blank=True)
    ftp_md5_password = models.CharField(_('ftp md5 password'),max_length=128,blank=True)

    AbstractUser.get_full_name.short_description = _("Full Name")


    @property
    def user_type(self):
        if str(self.polymorphic_ctype.model_class()).find("UserInstitutional") != -1:
            return _("Institutional")
        elif str(self.polymorphic_ctype.model_class()).find("UserEnterprise") != -1:
            return _("Enterprise")
        elif str(self.polymorphic_ctype.model_class()).find("UserGuest") != -1:
            return _("Guest")
        else:
            return _("Superuser")

    class Meta(AbstractUser.Meta):
        db_table = 'auth_user'
        swappable = 'AUTH_USER_MODEL'

class UserInstitutional(User):
    note = models.TextField(default="",blank=True)

    class Meta(User.Meta):
        db_table = 'auth_user_institutional'
        verbose_name = _('institutional user')
        verbose_name_plural = _('institutional users')

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.username, filename)

class UserEnterprise(User):
    enterprise_number = models.CharField(_('enterprise number'), max_length=10, default="",unique=True)
    ci_number = models.CharField(_('ci number'), max_length=11, default="",unique=True)
    phone_number = models.CharField(_('phone number'),max_length=20,default="",blank=True)
    extension_number = models.CharField(_('extension number'),max_length=10,default="",blank=True)
    authorized_document= models.FileField(_('authorized document'),upload_to=user_directory_path, blank=True)
    note = models.TextField(_('note'),blank=True)
    area = models.ForeignKey(Area,on_delete=models.SET_NULL, default=None, null=True)
    department = models.ForeignKey(Department,on_delete=models.SET_NULL, default=None, null=True)

    class Meta(User.Meta):
        db_table = 'auth_user_enterprise'
        verbose_name = _('enterprise user')
        verbose_name_plural = _('enterprise users')

class UserGuest(User):
    authorized_document = models.FileField(_('authorized document'), upload_to=user_directory_path, blank=True)
    note = models.TextField(_('note'), blank=True)

    class Meta(User.Meta):
        db_table = 'auth_user_guest'
        verbose_name = _('guest user')
        verbose_name_plural = _('guest users')