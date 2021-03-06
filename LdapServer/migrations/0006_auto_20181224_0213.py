# Generated by Django 2.1.3 on 2018-12-24 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LdapServer', '0005_auto_20181224_0208'),
    ]

    operations = [
        migrations.AddField(
            model_name='ldapserver',
            name='ftp_home',
            field=models.CharField(default='homeDrive', max_length=50, verbose_name='ftp home'),
        ),
        migrations.AddField(
            model_name='ldapserver',
            name='ftp_size',
            field=models.CharField(default='uidNumber', max_length=50, verbose_name='ftp size'),
        ),
        migrations.AlterField(
            model_name='ldapserver',
            name='internet_domain',
            field=models.CharField(default='employeeType', max_length=50, verbose_name='internet domain map'),
        ),
        migrations.AlterField(
            model_name='ldapserver',
            name='internet_extra_quota_size',
            field=models.CharField(default='telexNumber', max_length=50, verbose_name='internet extra quota size map'),
        ),
        migrations.AlterField(
            model_name='ldapserver',
            name='internet_quota_size',
            field=models.CharField(default='employeeNumber', max_length=50, verbose_name='internet quota size map'),
        ),
        migrations.AlterField(
            model_name='ldapserver',
            name='internet_quota_type',
            field=models.CharField(default='division', max_length=50, verbose_name='internet quota type map'),
        ),
    ]
