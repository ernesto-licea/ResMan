# Generated by Django 2.1.3 on 2018-12-24 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LdapServer', '0004_auto_20181224_0206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ldapserver',
            name='internet_extra_quota_size',
            field=models.CharField(default='telexNumber', max_length=50, verbose_name='proxy extra quota size map'),
        ),
    ]
