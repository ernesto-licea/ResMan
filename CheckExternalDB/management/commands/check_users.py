from django.core.management.base import BaseCommand

from CheckExternalDB.models import ExternalDB

class Command(BaseCommand):
    help = 'Check user status in external database and modify status in local database'

    def add_arguments(self, parser):
        parser.add_argument('external_name', type=str)

    def handle(self, *args, **options):
        external_name = options['external_name']

        try:
            external_db = ExternalDB.objects.get(name=external_name,is_active=True)
            status,changed_users,error = external_db.check_users()
            if not status:
                self.stdout.write(self.style.ERROR(error))
            else:
                if changed_users:
                    for obj in changed_users:
                        self.stdout.write(self.style.SUCCESS("username: %s, message: %s" % (obj['user'].username,obj['message'])))
                else:
                    self.stdout.write(self.style.SUCCESS("No user was modified as result of checking agains external database: %s" %external_name))
        except ExternalDB.DoesNotExist:
            self.stdout.write(self.style.ERROR("External Database with name: %s does not exist." %external_name))


