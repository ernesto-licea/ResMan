# Generated by Django 2.1.3 on 2018-12-08 05:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('EntStructure', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50, unique=True, verbose_name='name')),
                ('responsible', models.CharField(blank=True, default='', max_length=100, verbose_name='responsible')),
                ('email', models.EmailField(max_length=254, verbose_name='email area')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='EntStructure.Area')),
            ],
            options={
                'verbose_name': 'enterprise department',
                'verbose_name_plural': 'enterprise departments',
                'db_table': 'enterprise_departments',
            },
        ),
    ]