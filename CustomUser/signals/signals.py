import django.dispatch

save_ldap_user_signal = django.dispatch.Signal(providing_args=["obj"])
delete_ldap_user_signal = django.dispatch.Signal(providing_args=["obj"])
reset_user_password_signal = django.dispatch.Signal(providing_args=["obj"])
