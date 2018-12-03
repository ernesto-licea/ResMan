import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

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