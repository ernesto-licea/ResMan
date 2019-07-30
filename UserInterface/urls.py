from django.conf.urls import url
from UserInterface import views

urlpatterns = [
    # Dashboard main page
    url(r'^$', views.dashboard, name="dashboard"),
    url(r'^change_password$', views.change_password, name="change_password"),
    url(r'^logout/$', views.logout_view, name="logout"),
]
