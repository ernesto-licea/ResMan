import django.dispatch

save_ldap_user_signal = django.dispatch.Signal(providing_args=["obj","server"])
delete_ldap_user_signal = django.dispatch.Signal(providing_args=["obj"])
reset_user_password_signal = django.dispatch.Signal(providing_args=["obj","server"])
auth_ldap_user_signal = django.dispatch.Signal(providing_args=["obj","server"])
password_reset_successfully = django.dispatch.Signal(providing_args=["obj","admin_user","language_code"])
