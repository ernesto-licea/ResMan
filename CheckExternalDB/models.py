import base64
import pymssql
import MySQLdb
from django.db import models
from django.utils.translation import gettext_lazy as _
from CheckExternalDB.signals.signals import externaldb_check_user_signal
from CustomUser.models import UserEnterprise


class ExternalDB(models.Model):
    DB_TYPE = [
        ('mysql',_('MySQL Server')),
        ('sql', _('SQL Server'))
    ]

    USER_FIELDS = []
    for field in UserEnterprise._meta.fields:
        USER_FIELDS.append((field.name,field.verbose_name))

    USER_ACTION = [
        ('delete',_('Delete')),
        ('disable',_('Disable'))
    ]

    is_active = models.BooleanField(_('is active'), default=True)
    name = models.CharField(_('name'), max_length=100, default="", unique=True)
    db_type = models.CharField(_('type of database server'),choices=DB_TYPE,default=DB_TYPE[0][0],max_length=20)
    db_host = models.CharField(_('DB server'),default="",max_length=128)
    db_port = models.IntegerField(_('DB port'),default=3306)
    db_name = models.CharField(_('DB name'),default="",max_length=64)
    db_username = models.CharField(_('DB username'),default="",max_length=64)
    db_password = models.CharField(_('DB password'),default="",max_length=64)
    db_query = models.CharField(_('DB SQL query'),default="",max_length=1024,
                                help_text=_('You can use %s in your SQL query and it will be replaced for user field value chosen.'))
    user_field = models.CharField(_('user field'),choices=USER_FIELDS,default=USER_FIELDS[0][0],max_length=100)
    notify_informatics_staff = models.BooleanField(_('notify informatics staff?'), default=True)
    notify_supervisors_staff = models.BooleanField(_('notify supervisor staff?'), default=True)
    user_action = models.CharField(_('user action'),choices=USER_ACTION,default=USER_ACTION[0][0],max_length=20)
    email = models.EmailField(_('notification email'), default="", blank=True)
    creation_date = models.DateTimeField(_('creation date'),auto_now_add=True)
    description = models.TextField(_('description'),blank=True)

    def check_users(self):

        status = {
            'status':True,
            'user_changed':[],
            'error':''
        }
        try:
            user_changed = []
            user_list = UserEnterprise.objects.filter(status='active')
            for user in user_list:
                if self.db_type == 'sql':
                    conn = pymssql.connect(
                        host=self.db_host,
                        user=self.db_username,
                        password=base64.b64decode(self.db_password).decode('utf-8'),
                        database=self.db_name
                    )
                else:
                    conn = MySQLdb.connect(
                        host=self.db_host,
                        user=self.db_username,
                        passwd=base64.b64decode(self.db_password).decode('utf-8'),
                        db=self.db_name
                    )

                cursor = conn.cursor()
                cursor.execute(self.db_query %getattr(user,self.user_field))

                if not cursor.rowcount:
                    if self.user_action == 'delete':
                        ldap_error = user.delete()

                    else:
                        user.status = 'inactive'
                        user.save()
                        ldap_error = user.ldap_save()

                    if ldap_error:
                        user_changed.append(
                            {
                                'user': user,
                                'message': ldap_error
                            }
                        )
                    else:
                        user_changed.append(
                            {
                                'user': user,
                                'message': _('User: %(user)s was successfully %(action)s') % {
                                    'user': user.username,
                                    'action': _('Disabled') if self.user_action == 'disable' else _('Deleted')
                                }

                            }
                        )
                cursor.close()
                conn.close()
            status['user_changed'] = user_changed
            externaldb_check_user_signal.send(sender=self.__class__, externaldb=self, changed_users=user_changed)

        except Exception as e:
            status['status'] = False
            status['error'] = str(e)

        return [status['status'],status['user_changed'],status['error']]

    def check_connection(self):
        try:
            user = UserEnterprise.objects.filter(status='active').first()
            if self.db_type == 'sql':
                conn = pymssql.connect(
                    host=self.db_host,
                    user=self.db_username,
                    password=base64.b64decode(self.db_password).decode('utf-8'),
                    database=self.db_name
                )
            else:
                conn = MySQLdb.connect(
                    host=self.db_host,
                    user=self.db_username,
                    passwd=base64.b64decode(self.db_password).decode('utf-8'),
                    db=self.db_name
                )

            cursor = conn.cursor()
            cursor.execute(self.db_query %getattr(user,self.user_field))
            cursor.close()
            conn.close()
            return [True,'']
        except Exception as e:
            return [False,str(e)]

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'external_db'
        verbose_name = _('external database')
        verbose_name_plural = _('external databases')