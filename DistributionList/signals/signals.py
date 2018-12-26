import django.dispatch

create_ldap_distribution_list_signal = django.dispatch.Signal(providing_args=["distribution_list"])
modify_ldap_distribution_list_signal = django.dispatch.Signal(providing_args=["distribution_list"])