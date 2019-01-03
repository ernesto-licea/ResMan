import django.dispatch

create_ldap_group_signal = django.dispatch.Signal(providing_args=["service"])
modify_ldap_group_signal = django.dispatch.Signal(providing_args=["service"])