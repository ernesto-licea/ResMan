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
                _("This password must contain at least %(num_amount)d number%(plural)s.") %{
                    'num_amount': self.num_amount,
                    'plural': 's' if self.num_amount > 1 else ""
                },
                code='password_dont_have_number',

            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(num_amount)d number%(plural)s.") %{
                'num_amount': self.num_amount,
                'plural': 's' if self.num_amount > 1 else ""
            }

class MinimumUpperLetterAmount:
    def __init__(self, num_amount=1):
        self.num_amount = num_amount

    def validate(self, password, user=None):
        numbers = re.findall('[A-Z]', password)
        if len(numbers) < self.num_amount:
            raise ValidationError(
                _("This password must contain at least %(num_amount)d upper letter%(plural)s.") %{
                    'num_amount': self.num_amount,
                    'plural': 's' if self.num_amount > 1 else ""
                },
                code='password_dont_have_upper_letter',

            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(num_amount)d upper letter%(plural)s.") %{
                'num_amount': self.num_amount,
                'plural': 's' if self.num_amount > 1 else ""
            }

class MinimumSymbolAmount:
    def __init__(self, num_amount=1):
        self.num_amount = num_amount

    def validate(self, password, user=None):
        numbers = re.findall('\W', password)
        if len(numbers) < self.num_amount:
            raise ValidationError(
                _("This password must contain at least %(num_amount)d symbol%(plural)s.") %{
                    'num_amount': self.num_amount,
                    'plural': 's' if self.num_amount > 1 else ""
                },
                code='password_dont_have_symbol',

            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(num_amount)d symbol%(plural)s.") %{
                'num_amount': self.num_amount,
                'plural': 's' if self.num_amount > 1 else ""
            }

class RepeatPasswordAmount:
    def __init__(self, num_amount=1):
        self.num_amount = num_amount

    def validate(self, password, user=None):
        if user:
            password_history = user.passwordhistory_set.all()

            if check_password(password,user.password):
                raise ValidationError(
                    _("This password can not be the current password."),
                    code='current_password_used',
                )

            for history in password_history:
                if check_password(password,history.password):
                    raise ValidationError(
                        _("This password can not be the current password or the last %(num_amount)s password%(plural)s used previously.") %{
                            'num_amount': str(self.num_amount-1) if self.num_amount > 2 else "",
                            'plural': 's' if self.num_amount > 2 else ""
                        },
                        code='password_used',
                    )

    def password_changed(self,password, user=None):
        if user:
            # Remove old histories of passwords
            password_history = user.passwordhistory_set.all()
            if password_history.count() > self.num_amount:
                for a in password_history[:password_history.count() - self.num_amount]:
                    a.delete()



    def get_help_text(self):
        return _(
            "Your can not use the current password or the last %(num_amount)s password%(plural)s used previously.") %{
                'num_amount': str(self.num_amount-1) if self.num_amount > 2 else "",
                'plural': 's' if self.num_amount > 2 else ""
            }
