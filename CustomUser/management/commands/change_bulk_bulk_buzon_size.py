import base64

from django.core.management.base import BaseCommand, CommandError

from CustomUser.models import UserEnterprise, User, PasswordHistory


class Command(BaseCommand):
    help = 'Migrate from ums database'

    def add_arguments(self, parser):
        parser.add_argument('email_buzon_size', type=int)

    def handle(self, *args, **options):
        email_buzon_size = options['email_buzon_size']

        count_users = 0

        for enterprise_user in UserEnterprise.objects.filter(status='active'):
            enterprise_user.email_buzon_size = email_buzon_size
            enterprise_user.save()
            count_users += 1
            message = "User: {} was modified successfully".format(enterprise_user.get_full_name())
            self.stdout.write(self.style.SUCCESS(message))

        total_size = count_users*email_buzon_size
        unity = "MB"
        if total_size > 1024:
            total_size = total_size/1024
            unity = "GB"

        message = "Total users modified: {}. You need at least {} {} of space in your server".format(
            count_users,
            total_size,
            unity
        )
        self.stdout.write(self.style.SUCCESS(message))
