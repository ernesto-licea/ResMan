# Generated by Django 2.1.3 on 2018-12-11 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DistributionList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50, unique=True, verbose_name='name')),
                ('responsible', models.CharField(blank=True, default='', max_length=100, verbose_name='responsible')),
                ('email', models.EmailField(max_length=254, verbose_name='email area')),
                ('slugname', models.SlugField(default='', verbose_name='slugname')),
            ],
            options={
                'verbose_name': 'enterprise distribution list',
                'verbose_name_plural': 'enterprise distribution lists',
                'db_table': 'enterprise_distribution_list',
            },
        ),
    ]
