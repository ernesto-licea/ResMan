# Generated by Django 2.1.3 on 2018-12-29 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CustomUser', '0008_userenterprise_department'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='proxy_domain',
        ),
        migrations.RemoveField(
            model_name='user',
            name='proxy_extra_quota_size',
        ),
        migrations.RemoveField(
            model_name='user',
            name='proxy_quota_size',
        ),
        migrations.RemoveField(
            model_name='user',
            name='proxy_quota_type',
        ),
        migrations.AddField(
            model_name='user',
            name='internet_domain',
            field=models.CharField(blank=True, choices=[('local', 'Local'), ('national', 'National'), ('international', 'International')], default='local', max_length=20, verbose_name='internet domain reach'),
        ),
        migrations.AddField(
            model_name='user',
            name='internet_extra_quota_size',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='internet extra quota size'),
        ),
        migrations.AddField(
            model_name='user',
            name='internet_quota_size',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='internet quota size'),
        ),
        migrations.AddField(
            model_name='user',
            name='internet_quota_type',
            field=models.CharField(blank=True, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='daily', max_length=20, verbose_name='internet quota type'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email_buzon_size',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='email buzon size'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email_message_size',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='email messages size'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=30, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='ftp_size',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='ftp size'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=150, verbose_name='last name'),
        ),
    ]