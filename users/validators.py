from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date


def date_of_birth_validator(date_param):
    """ Check if a user's age is zero or less """
    today = date.today()
    born = date_param
    years_now = today.year - born.year - \
        ((today.month, today.day) < (born.month, born.day))
    if years_now < 15:
        raise ValidationError(
            _('You cannot have less than 15 years'),
            params={'date_param': date_param},
        )
    elif years_now > 100:
        raise ValidationError(
            _('You cannot have more than 100 years'),
            params={'date_param': date_param}
        )
