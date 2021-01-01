from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms.widgets import DateInput
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from .models import CustomUser
from .validators import date_of_birth_validator


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('name_surname', 'username', 'email', 'country',
                  'date_of_birth')
        widgets = {'date_of_birth': DateInput(attrs={'type': 'date'})}


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class EditUser(forms.Form):
    name_surname = forms.CharField(label="Full Name", max_length=180)
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="New password", widget=forms.PasswordInput(), required=False)
    country = CountryField(blank_label='Country').formfield()
    date_of_birth = forms.DateField(label="Birthday", validators=[
                                    date_of_birth_validator],
                                    widget=DateInput(attrs={'type': 'date'}))
    GENDER_OPTIONS = (
        ('m', 'Male'),
        ('f', 'Female')
    )
    gender = forms.ChoiceField(
        choices=GENDER_OPTIONS, required=False)
    website = forms.CharField(label="My website", required=False)
    about_me = forms.CharField(label="About Me",
                               required=False, widget=forms.Textarea(
                                   attrs={'rows': 5}),
                               max_length=500)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            try:
                password_validation.validate_password(password)
            except forms.ValidationError as error:
                self.add_error('password', error)
        return password
