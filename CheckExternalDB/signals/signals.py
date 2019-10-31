import django.dispatch

externaldb_check_user_signal = django.dispatch.Signal(providing_args=["externaldb","changed_users"])