import base64

import MySQLdb
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from CustomUser.models import UserEnterprise, User, PasswordHistory
from EntStructure.models import Area, Department
from Services.models import Service


class Command(BaseCommand):
    help = 'Migrate from ums database'

    def add_arguments(self, parser):
        parser.add_argument('db_host', type=str)
        parser.add_argument('db_name', type=str)
        parser.add_argument('db_user', type=str)
        parser.add_argument('db_passwd', type=str)

    def handle(self, *args, **options):
        db_host = options['db_host']
        db_name = options['db_name']
        db_user = options['db_user']
        db_passwd = options['db_passwd']


        serv_internet = Service.objects.get(name='Internet')
        serv_mail = Service.objects.get(name='Email')
        serv_chat = Service.objects.get(name='Chat')

        #Crear Lista de Distribución Todos
        try:
            todos = Service.objects.get(name="Todos")
        except Service.DoesNotExist:
            todos = Service.objects.create(
                name="Todos",
                service_type="distribution",
                email="todos@cnic.cu",
                description="Lista de distribución que incluye todos los usuarios del sistema.",
                slugname='todos'
            )

            self.stdout.write(self.style.SUCCESS("Distribution List: %s" %todos.name))



        email_account_type = 'local'
        account_type_dicc = {
            'local':'local',
            'nacional':'national',
            'internacional':'international'
        }




        con = MySQLdb.connect(host=db_host, user=db_user, passwd=db_passwd, db=db_name)
        c = con.cursor()
        c.execute("Select * from accounts_account where active=1")
        count = 0
        for user_row in c.fetchall():
            internet_service = False
            mail_service = False
            chat_service = False


            id = user_row[0]
            active = user_row[1]
            active_begin = user_row[2]
            active_end = user_row[3]
            personal_ID = user_row[4]
            first_name = user_row[5]
            last_name = user_row[6]
            username = user_row[7]
            password = user_row[8]
            check_password = user_row[9]
            entity_ID = user_row[10]
            telephone = user_row[11]
            department_id = user_row[12]
            created = user_row[13]
            modified = user_row[14]

            #Buscar si tiene cuenta de internet
            c.execute("select * from accounts_proxyaccount where account_id=%d and proxy_active=1" %id)
            if c.rowcount > 0:
                internet_service = True

            #Buscar si tiene cuenta de correo
            c.execute("select * from accounts_mailaccount where account_id=%d and mail_active=1" %id)
            if c.rowcount > 0:
                mail_service = True
                email_row = c.fetchone()

                email = email_row[5]

                #Obtener tipo de cuenta de correo
                account_type_id = email_row[9]
                c.execute("select * from accounts_mailaccounttype where id = %d" %account_type_id)
                email_account_type_row = c.fetchone()
                email_account_type = email_account_type_row[1]

            #Buscar si tiene cuenta de chat
            c.execute("select * from accounts_jabberaccount where account_id=%d and jabber_active=1" %id)
            if c.rowcount > 0:
                chat_service = True

            #Buscar Departamento
            c.execute("select * from accounts_department where id=%d" %department_id)
            department_row = c.fetchone()
            department_name = department_row[1]
            area_id = department_row[2]

            #Buscar Area
            c.execute("select * from accounts_area where id=%d" %area_id)
            area_row = c.fetchone()
            area_name = area_row[1]

            #Crear Area si no existe
            try:
                area = Area.objects.get(name=area_name)
            except Area.DoesNotExist:
                area = Area.objects.create(
                    name=area_name,
                    slugname=slugify(area_name)
                )
                self.stdout.write(self.style.SUCCESS("Area: %s" %area.name))

            #Crear Dpto si no existe
            try:
                dpto = Department.objects.get(name=department_name,area=area)
            except:
                dpto = Department.objects.create(
                    name=department_name,
                    area=area,
                    slugname=slugify(department_name)
                )
                self.stdout.write(self.style.SUCCESS("Department: %s" %dpto.name))

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                UserEnterprise.objects.create_user(
                    username=username,
                    email='%s@%s' %(username,'cnic.cu'),
                    password='Adminadmin505*',
                )

            user = UserEnterprise.objects.get(username=username)
            user.status='active'
            user.username=username
            user.first_name=first_name
            user.last_name=last_name
            user.ci_number=personal_ID.replace(" ","")
            user.enterprise_number=entity_ID.replace(" ","")
            user.area=area
            user.department=dpto
            user.email_domain = account_type_dicc[email_account_type]
            user.internet_domain = 'international'
            user.session_key = base64.b64encode("Adminadmin505*".encode('utf-8')).decode()

            user_services = []
            if internet_service:
                user_services.append(serv_internet)
            if mail_service:
                user_services.append(serv_mail)

            if chat_service:
                user_services.append(serv_chat)


            for s in user_services:
                user.services.add(s)

            user.distribution_list.add(todos)

            self.stdout.write(self.style.SUCCESS("User: %s, CI: %s" % (user.username,user.ci_number)))

            user.save()

            PasswordHistory.objects.create(user=user, password=user.password)

            self.stdout.write(self.style.SUCCESS("User: %s, Email Type: %s" % (user.username,user.email_domain)))


            count += 1


        self.stdout.write(self.style.SUCCESS("%d" %count))
