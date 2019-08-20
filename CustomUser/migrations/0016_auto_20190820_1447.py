# Generated by Django 2.1.3 on 2019-08-20 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CustomUser', '0015_auto_20190819_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='userenterprise',
            name='outside',
            field=models.BooleanField(default=False, verbose_name='Is Outside?'),
        ),
        migrations.AlterField(
            model_name='user',
            name='distribution_list',
            field=models.ManyToManyField(blank=True, help_text='', limit_choices_to={'is_active': True, 'service_type': 'distribution'}, related_name='distribution_list_set', related_query_name='distribution_list', to='Services.Service', verbose_name='distribution list'),
        ),
        migrations.AlterField(
            model_name='user',
            name='services',
            field=models.ManyToManyField(blank=True, help_text='', limit_choices_to={'is_active': True, 'service_type': 'security'}, related_name='services_set', related_query_name='services', to='Services.Service', verbose_name='services'),
        ),
    ]
