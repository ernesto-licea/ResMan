from django.conf.urls import url
from UserInterface import views

urlpatterns = [
    # Dashboard main page
    url(r'^$', views.dashboard, name="dashboard"),
    url(r'^change_password$', views.change_password, name="change_password"),
    url(r'^supervision/users$', views.supervision_users, name="supervision_users"),
    url(r'^supervision/services$', views.supervision_services, name="supervision_services"),
    url(r'^supervision/distribution_list$', views.supervision_distribution_list, name="supervision_distribution_list"),
    url(r'^logout/$', views.logout_view, name="logout"),
]
