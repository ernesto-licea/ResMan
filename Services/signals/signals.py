import django.dispatch

save_ldap_group_signal = django.dispatch.Signal(providing_args=["obj","server"])
delete_ldap_group_signal = django.dispatch.Signal(providing_args=["obj"])