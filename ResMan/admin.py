from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class ResManAdminSite(AdminSite):
    site_header = _("ResMan- User Management System")
    site_title = _("ResMan- User Management System")

admin_site = ResManAdminSite(name='myadmin')
