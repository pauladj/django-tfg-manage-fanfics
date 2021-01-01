from ..forms import CustomUserCreationForm, EditUser
from django.test import TestCase
from datetime import date


class CustomUserCreationFormTests(TestCase):

    def test_valid_form(self):
        data = {'name_surname': "Testing test", 'username': "testinguser",
                'email': 'test@test.com', 'country': 'US',
                'date_of_birth': '1997-07-08', 'password1': 'A1.aaaaa',
                'password2': 'A1.aaaaa'}
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_birthday_form(self):
        data = {'name_surname': "Testing test", 'username': "testinguser",
                'email': 'test@test.com', 'country': 'US',
                'date_of_birth': date.today(), 'password1': 'A1.aaaaa',
                'password2': 'A1.aaaaa'}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())


class EditUserCreationFormTests(TestCase):

    def test_valid_form(self):
        data = {'name_surname': "Testing test", 'country': 'US',
                'date_of_birth': '1997-07-08', 'gender': 'f',
                'email': 'newEmail@gm.com',
                'website': 'good-url', 'about_me': "blah blah"}
        form = EditUser(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_country_form(self):
        data = {'name_surname': "Testing test", 'country': 'invalid-country',
                'email': 'newEmail@gm.com',
                'date_of_birth': '1997-07-08', 'gender': 'f',
                'website': 'good-url', 'about_me': "blah blah"}
        form = EditUser(data=data)
        self.assertFalse(form.is_valid())
