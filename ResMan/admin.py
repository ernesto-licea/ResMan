from django.contrib.admin import AdminSite

class ResManAdminSite(AdminSite):
    site_header = 'Monty Python administration'

admin_site = ResManAdminSite(name='myadmin')
