import django.dispatch

create_ldap_user_signal = django.dispatch.Signal(providing_args=["user"])
modify_ldap_user_signal = django.dispatch.Signal(providing_args=["user"])