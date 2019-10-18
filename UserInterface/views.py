import base64
import hashlib
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext

from CustomUser.models import User, PasswordHistory
from LdapServer.models import LdapServer
from Services.models import Service
from UserInterface.forms import LoginForm, UserPasswordChangeForm


def get_default_data(request):
    if request.user.is_anonymous:
        return {
            "user":request.user
        }
    else:
        return {
            'user':request.user,
            "service_list": request.user.services.filter(is_active=True),
            "distribution_list": request.user.distribution_list.filter(is_active=True),
        }


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

                        if ldap_servers:
                            # Se detiene con el primer servidor ldap que autentique
                            is_ldap_auth = db_user.auth_ldap(password)

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
                            user = authenticate(username=username, password=password)
                            if user is not None:
                                login(request, user)
                                return HttpResponseRedirect(reverse("dashboard"))
                            else:
                                error = True
                    else:
                        user = authenticate(username=username,password=password)
                        if user is not None:
                            login(request,user)
                            return HttpResponseRedirect(reverse("dashboard"))
                        else:
                            error = True

                except User.DoesNotExist:
                    error = True

        else:
            form = LoginForm()

        data = get_default_data(request)
        data.update({
            "error": error,
            "form": form,
        })

        return render(request, 'UserInterface/dashboard.html', data)

    else:
        #Servir pagina logueado con los datos del usuario
        data = get_default_data(request)

    return render(request, 'UserInterface/dashboard.html', data)


def change_password(request):
    if request.user.is_authenticated:
        message_success = False
        message_error = False


        if request.method == 'POST':
            form = UserPasswordChangeForm(request.user, request.POST)
            if form.is_valid():

                password = form.cleaned_data.get('new_password2')
                user = form.save(commit=False)
                user._password = password

                ldap_error = user.ldap_reset_password(password)
                if ldap_error:
                    message_error = ldap_error
                else:
                    hash_password = make_password(password)
                    PasswordHistory.objects.create(user=user, password=hash_password)

                    user.password_date = timezone.now()
                    user.ftp_md5_password = hashlib.md5(user._password.encode('utf-8')).hexdigest()
                    user.session_key = base64.b64encode(user._password.encode('utf-8')).decode()

                    user.save()
                    message_success = gettext('Password changed successfully.')

                    update_session_auth_hash(request, form.user)
        else:
            form = UserPasswordChangeForm(request.user)

        data = get_default_data(request)
        data.update({
            'form':form,
            'message_error':message_error,
            'message_success':message_success,
        })

        return render(request, 'UserInterface/password.html', data)
    else:
        return HttpResponseRedirect(reverse('dashboard'))

def supervision_users(request):
    data = get_default_data(request)

    page = request.GET.get('page')
    search = request.GET.get('q')

    if not page:
        page = 1

    if not search:
        search = ""

    if search:
        object_list = User.objects.filter(username__icontains=search).order_by('-date_joined')
    else:
        object_list = User.objects.all().order_by('-date_joined')
    p = Paginator(object_list, 25)



    if int(page) > p.num_pages:
        page = p.num_pages

    if int(page)<=5:
        initial = 1
    else:
        initial = int((int(page)-1)/5)
        initial = initial*5 +1

    if p.num_pages <= 5:
        end = p.num_pages + 1
    else:
        end = initial + 5 if initial+5 < p.num_pages else p.num_pages + 1


    data.update({
        'objects':p.get_page(page),
        'page_show_range':range(int(initial),int(end)),
        'search':search,
        'users_menu':'active'
    })
    return render(request, 'UserInterface/supervision_users.html', data)

def supervision_services(request):
    data = get_default_data(request)

    page = request.GET.get('page')
    search = request.GET.get('q')

    if not page:
        page = 1

    if not search:
        search = ""

    if search:
        object_list = Service.objects.filter(name__icontains=search,is_active=True,service_type='security').order_by("-id")
    else:
        object_list = Service.objects.filter(is_active=True,service_type='security').order_by("-id")
    p = Paginator(object_list, 5)

    if int(page) > p.num_pages:
        page = p.num_pages

    if int(page) <= 5:
        initial = 1
    else:
        initial = int((int(page) - 1) / 5)
        initial = initial * 5 + 1

    if p.num_pages <= 5:
        end = p.num_pages + 1
    else:
        end = initial + 5 if initial + 5 < p.num_pages else p.num_pages + 1

    data.update({
        'objects': p.get_page(page),
        'page_show_range': range(int(initial), int(end)),
        'search': search,
        'services_menu': 'active'
    })
    return render(request, 'UserInterface/supervision_services.html', data)

def supervision_distribution_list(request):
    data = get_default_data(request)

    page = request.GET.get('page')
    search = request.GET.get('q')

    if not page:
        page = 1

    if not search:
        search = ""

    if search:
        object_list = Service.objects.filter(name__icontains=search,is_active=True,service_type='distribution').order_by("-id")
    else:
        object_list = Service.objects.filter(is_active=True,service_type='distribution').order_by("-id")
    p = Paginator(object_list, 5)

    if int(page) > p.num_pages:
        page = p.num_pages

    if int(page) <= 5:
        initial = 1
    else:
        initial = int((int(page) - 1) / 5)
        initial = initial * 5 + 1

    if p.num_pages <= 5:
        end = p.num_pages + 1
    else:
        end = initial + 5 if initial + 5 < p.num_pages else p.num_pages + 1

    data.update({
        'objects': p.get_page(page),
        'page_show_range': range(int(initial), int(end)),
        'search': search,
        'distribution_list_menu': 'active'
    })
    return render(request, 'UserInterface/supervision_distribution_list.html', data)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("dashboard"))
