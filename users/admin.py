from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('name_surname', 'email', 'country',
                                         'date_of_birth', 'gender')}),
        (_('Other info'), {'fields': ('website', 'about_me', 'avatar')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name_surname', 'username', 'email', 'country',
                       'date_of_birth', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'name_surname',
                    'date_of_birth', 'country', 'gender',
                    'is_staff')
    search_fields = ('username', 'name_surname', 'email')
    ordering = ('username', 'country', 'gender', 'is_staff')


admin.site.register(CustomUser, CustomUserAdmin)

