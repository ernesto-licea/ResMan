# Generated by Django 2.1.3 on 2018-12-06 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CustomUser', '0005_auto_20181203_0108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userenterprise',
            name='ci_number',
            field=models.CharField(default='', max_length=11, unique=True, verbose_name='ci number'),
        ),
        migrations.AlterField(
            model_name='userenterprise',
            name='enterprise_number',
            field=models.CharField(default='', max_length=10, unique=True, verbose_name='enterprise number'),
        ),
    ]
