# Generated by Django 2.1.3 on 2019-10-24 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalDB',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('outside', models.BooleanField(default=False, help_text='Check this options if user is outside of the county.', verbose_name='Is Outside?')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('name', models.CharField(default='', max_length=100, unique=True, verbose_name='name')),
                ('db_type', models.CharField(choices=[('mysql', 'MySQL Server'), ('sql', 'SQL Server')], default='mysql', max_length=20, verbose_name='type of database server')),
                ('db_host', models.CharField(default='', max_length=128, verbose_name='db server')),
                ('db_port', models.IntegerField(default=3306, verbose_name='db port')),
                ('db_name', models.CharField(default='', max_length=64, verbose_name='db name')),
                ('db_username', models.CharField(default='', max_length=64, verbose_name='db username')),
                ('db_password', models.CharField(default='', max_length=64, verbose_name='db password')),
                ('db_query', models.CharField(default='', max_length=1024, verbose_name='db SQL query')),
                ('user_field', models.CharField(choices=[('id', 'id'), ('password', 'password'), ('last_login', 'last_login'), ('is_superuser', 'is_superuser'), ('username', 'username'), ('is_active', 'is_active'), ('date_joined', 'date_joined'), ('polymorphic_ctype', 'polymorphic_ctype'), ('is_staff', 'is_staff'), ('is_supervisor', 'is_supervisor'), ('status', 'status'), ('password_date', 'password_date'), ('first_name', 'first_name'), ('last_name', 'last_name'), ('email', 'email'), ('email_buzon_size', 'email_buzon_size'), ('email_message_size', 'email_message_size'), ('email_domain', 'email_domain'), ('internet_quota_type', 'internet_quota_type'), ('internet_quota_size', 'internet_quota_size'), ('internet_extra_quota_size', 'internet_extra_quota_size'), ('internet_domain', 'internet_domain'), ('ftp_folder', 'ftp_folder'), ('ftp_size', 'ftp_size'), ('ftp_md5_password', 'ftp_md5_password'), ('session_key', 'session_key'), ('area', 'area'), ('department', 'department'), ('user_ptr', 'user_ptr'), ('enterprise_number', 'enterprise_number'), ('ci_number', 'ci_number'), ('phone_number', 'phone_number'), ('extension_number', 'extension_number'), ('authorized_document', 'authorized_document'), ('note', 'note'), ('outside', 'outside')], default='id', max_length=100, verbose_name='user field')),
                ('user_action', models.CharField(choices=[('delete', 'Delete'), ('Disable', 'Disable')], default='delete', max_length=20, verbose_name='user action')),
                ('email', models.EmailField(blank=True, default='', max_length=254, verbose_name='notification email')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('description', models.TextField(blank=True, verbose_name='description')),
            ],
            options={
                'verbose_name': 'external DB',
                'db_table': 'external_db',
            },
        ),
    ]
