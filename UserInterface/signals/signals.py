import django.dispatch

password_changed_successfully = django.dispatch.Signal(providing_args=["obj","language_code"])
