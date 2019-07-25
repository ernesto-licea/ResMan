import base64
import hashlib

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from CustomUser.models import User, PasswordHistory
from LdapServer.models import LdapServer
from UserInterface.forms import LoginForm


def dashboard(request):
    if request.user.is_anonymous:
        error = False

        #Servir pagina para loguearse
        #Logica para loguearse
        if request.method == "POST":
            form = LoginForm(request.POST)

            #Obtener datos del formulario
            if form.is_valid():
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                remember_me = form.cleaned_data["remember_me"]

                try:
                    db_user = User.objects.get(username=username,status__in=['active','blocked'])
                    if db_user.status == "active":
                        ldap_servers = LdapServer.objects.filter(is_active=True)

                        # Se detiene con el primer servidor ldap que autentique
                        is_ldap_auth = False
                        for ldap_server in ldap_servers:
                            is_ldap_auth = ldap_server.authenticate(username,password)
                            if is_ldap_auth:
                                break

                        if is_ldap_auth:
                            user = authenticate(username=username,password=password)
                            if user is not None:
                                login(request,user)
                                return HttpResponseRedirect(reverse("dashboard"))
                            else:
                                # Cambiar ultimo password para que coincida con ldap
                                db_user.set_password(password)
                                hash_password = make_password(password)
                                password_history = PasswordHistory.objects.filter(user=db_user).last()
                                password_history.password = hash_password
                                password_history.save()

                                db_user.ftp_md5_password = hashlib.md5(password.encode('utf-8')).hexdigest()
                                db_user.session_key = base64.b64encode(password.encode('utf-8')).decode()

                                db_user._password = password
                                db_user.save()

                                user = authenticate(username=username,password=password)
                                login(request,user)
                                return HttpResponseRedirect(reverse("dashboard"))
                        else:
                            error = True
                    else:
                        user = authenticate(username=username,password=password)
                        print(user)
                        if user is not None:
                            login(request,user)
                            return HttpResponseRedirect(reverse("dashboard"))
                        else:
                            error = True

                except User.DoesNotExist:
                    error = True

        else:
            form = LoginForm()

        data = {
            "error":error,
            "form":form,
            "user":request.user
        }
        return render(request, 'UserInterface/index.html', data)

    else:
        #Servir pagina logueado con los datos del usuario
        data = {
            "user": request.user
        }

    return render(request, 'UserInterface/index.html', data)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("dashboard"))
