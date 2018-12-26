import django.dispatch

create_ldap_service_signal = django.dispatch.Signal(providing_args=["service"])
modify_ldap_service_signal = django.dispatch.Signal(providing_args=["service"])