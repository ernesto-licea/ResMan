import django.dispatch

create_ldap_group_signal = django.dispatch.Signal(providing_args=["obj"])
modify_ldap_group_signal = django.dispatch.Signal(providing_args=["obj"])