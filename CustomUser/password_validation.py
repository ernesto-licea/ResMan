import re

from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from CustomUser.models import PasswordHistory


class MinimumNumAmount:
    def __init__(self, num_amount=1):
        self.num_amount = num_amount

    def validate(self, password, user=None):
        numbers = re.findall('\d', password)
        if len(numbers) < self.num_amount:
            raise ValidationError(
                _("This password must contain at least %(num_amount)d number%(plural)s."),
                code='password_dont_have_number',
                params={
                    'num_amount': self.num_amount,
                    'plural': 's' if self.num_amount > 1 else ""
                },
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(num_amount)d number%(plural)s."
            %{
                'num_amount': self.num_amount,
                'plural': 's' if self.num_amount > 1 else ""
            }
        )
class MinimumUpperLetterAmount:
    def __init__(self, num_amount=1):
        self.num_amount = num_amount

    def validate(self, password, user=None):
        numbers = re.findall('[A-Z]', password)
        if len(numbers) < self.num_amount:
            raise ValidationError(
                _("This password must contain at least %(num_amount)d upper letter%(plural)s."),
                code='password_dont_have_upper_letter',
                params={
                    'num_amount': self.num_amount,
                    'plural': 's' if self.num_amount > 1 else ""
                },
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(num_amount)d upper letter%(plural)s."
            %{
                'num_amount': self.num_amount,
                'plural': 's' if self.num_amount > 1 else ""
            }
        )
class MinimumSymbolAmount:
    def __init__(self, num_amount=1):
        self.num_amount = num_amount

    def validate(self, password, user=None):
        numbers = re.findall('\W', password)
        if len(numbers) < self.num_amount:
            raise ValidationError(
                _("This password must contain at least %(num_amount)d symbol%(plural)s."),
                code='password_dont_have_symbol',
                params={
                    'num_amount': self.num_amount,
                    'plural': 's' if self.num_amount > 1 else ""
                },
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(num_amount)d symbol%(plural)s."
            %{
                'num_amount': self.num_amount,
                'plural': 's' if self.num_amount > 1 else ""
            }
        )

class RepeatPasswordAmount:
    def __init__(self, num_amount=1):
        self.num_amount = num_amount

    def validate(self, password, user=None):
        if user:
            password_history = user.passwordhistory_set.all()

            for history in password_history:
                if check_password(password,history.password):
                    raise ValidationError(
                        _("This password can not be the same last %(num_amount)d password%(plural)s used."),
                        code='password_used',
                        params={
                            'num_amount': self.num_amount,
                            'plural': 's' if self.num_amount > 1 else ""
                        },
                    )

    def password_changed(self,password, user=None):
        if user:
            #Create history del new password
            hash_password = make_password(password)
            PasswordHistory.objects.create(user=user, password=hash_password)
            # Remove old histories of passwords
            password_history = user.passwordhistory_set.all()
            if password_history.count() > self.num_amount:
                for a in password_history[:password_history.count() - self.num_amount]:
                    a.delete()



    def get_help_text(self):
        return _(
            "Your can not use the last %(num_amount)d password%(plural)s"
            %{
                'num_amount': self.num_amount,
                'plural': 's' if self.num_amount > 1 else ""
            }
        )