"""ResMan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static

from ResMan.admin import admin_site
from django.urls import path
from django.conf.urls import include, url
from UserInterface.views import change_password

urlpatterns = [
    path(
        'admin/password_change/',
        change_password,
        name='admin_password_change',
    ),
    path('admin/', admin_site.urls),
    url(r'',include("UserInterface.urls"))
]
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)