import logging

from django import forms
from django.core.exceptions import ValidationError

# Get an instance of a logger
logger = logging.getLogger(__name__)


def clean_string(string_to_clean):
    ''' Cleans the string. It returns None if there's a problem or empty '''
    f = forms.CharField(required=True)
    try:
        clean_string = f.clean(string_to_clean)
        return clean_string
    except ValidationError:
        return None


def clean_integer(number):
    ''' Cleans the number. If error or it's not a number none '''
    f = forms.IntegerField(required=True)
    try:
        integer = f.clean(number)
        return integer
    except ValidationError:
        return None


class CustomError(Exception):
    pass

