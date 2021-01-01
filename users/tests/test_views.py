from unittest import mock

from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from common.models import Type, Fandom, Fanfic, Character, FandomFanfic, \
    CharacterFanfic
from ..models import CustomUser


class SignUpTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(name_surname="Testing user",
                                              username="testuser",
                                              email="test@test",
                                              country="US",
                                              date_of_birth="1997-07-08",
                                              password="A1.aaaaa")

    def test_sign_up_status_code(self):
        response = self.client.get(reverse('signup'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_uses_correct_template(self):
        response = self.client.get(reverse('signup'))
        self.assertTemplateUsed(response, 'signup.html')

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_ajax')
    def test_username_exists(self, mock_is_ajax):
        mock_is_ajax.response_value = True
        c = Client()
        response = c.get(reverse('check_username'), {'username': 'testuser'})
        self.assertEqual(response.status_code, 404)

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_ajax')
    def test_username_does_not_exists(self, mock_is_ajax):
        mock_is_ajax.response_value = True
        c = Client()
        response = c.get(reverse('check_username'), {
            'username': 'testusernotexists'})
        self.assertEqual(response.status_code, 200)

    def test_username_not_allowed(self):
        c = Client()
        response = c.get(reverse('check_username'))
        self.assertEqual(response.status_code, 405)


class SignUpDoneTests(SimpleTestCase):

    def test_sign_up_done_status_code(self):
        response = self.client.get(reverse('signup_done'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_done_uses_correct_template(self):
        response = self.client.get(reverse('signup_done'))
        self.assertTemplateUsed(response, 'signup_done.html')


class LogInTests(SimpleTestCase):

    def test_log_in_status_code(self):
        response = self.client.get(reverse('login'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_log_in_done_uses_correct_template(self):
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'registration/login.html')


class LogOutTests(SimpleTestCase):

    def test_log_out_status_code(self):
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)


class PasswordResetTests(SimpleTestCase):

    def test_pswd_reset_status_code(self):
        response = self.client.get(reverse('password_reset'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_pswd_reset_correct_template(self):
        response = self.client.get(reverse('password_reset'))
        self.assertTemplateUsed(response,
                                'registration/password_reset_form.html')

    def test_pswd_reset_done_status_code(self):
        response = self.client.get(reverse('password_reset_done'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_pswd_reset_done_correct_template(self):
        response = self.client.get(reverse('password_reset_done'))
        self.assertTemplateUsed(response,
                                'registration/password_reset_done.html')

    def test_pswd_reset_complete_status_code(self):
        response = self.client.get(reverse('password_reset_complete'),
                                   follow=True)
        self.assertEqual(response.status_code, 200)

    def test_pswd_reset_complete_correct_template(self):
        response = self.client.get(reverse('password_reset_complete'))
        self.assertTemplateUsed(response,
                                'registration/password_reset_complete.html')


class EditUserSettingsTests(TestCase):

    def setUp(self):
        self.normal_user = CustomUser.objects.create(
            name_surname="name",
            country="AM",
            date_of_birth="2000-07-02",
            email="em@gm.com",
            username='testuser',
            password="12345")

        self.client = Client()
        self.client.force_login(user=self.normal_user)

    def test_get_profile_user_settings_page(self):
        """ Check if the profile page is ok """
        response = self.client.get(reverse('edit_profile_user', kwargs={
            'user_id': self.normal_user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit-user.html')

    def test_put_profile_user_settings_page(self):
        """ Check if the data is correctly updated """
        data = {
            "_method": "put",
            "name_surname": "new_name",
            "country": "US",
            "email": "newemail@gmail.com",
            "date_of_birth": "2000-07-02"
        }

        response = self.client.post(reverse('edit_profile_user', kwargs={
            'user_id': self.normal_user.id}), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit-user.html')

        test_user = CustomUser.objects.get(username='testuser')
        self.assertEqual("new_name", test_user.name_surname)

    def test_get_profile_user_general_page(self):
        """ Check if the general page is ok """
        response = self.client.get(reverse('edit_general_user', kwargs={
            'user_id': self.normal_user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit-user.html')

    def test_put_general_user_settings_page(self):
        """ Check if the data is correctly updated """
        data = {
            "_method": "put",
            "rsvp": "1",
        }

        response = self.client.post(reverse('edit_general_user', kwargs={
            'user_id': self.normal_user.id}), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit-user.html')

        test_user = CustomUser.objects.get(username='testuser')
        self.assertEqual(1, test_user.privacy)


class ProfileTests(TestCase):

    def setUp(self):
        self.normal_user = CustomUser.objects.create(
            name_surname="name",
            country="AM",
            date_of_birth="2000-07-02",
            email="em@gm.com",
            username='testuser',
            password="12345")

        self.normal_user2 = CustomUser.objects.create(
            name_surname="name2",
            country="AM",
            date_of_birth="2000-07-02",
            email="em2@gm.com",
            username='testuser2',
            password="12345")

        self.client = Client()
        self.client.force_login(user=self.normal_user)

    def test_get_profile(self):
        """ Check if the profile page is ok """
        response = self.client.get(reverse('profile', kwargs={
            'user_id': self.normal_user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_ajax')
    def test_if_user_is_following_another(self, mock_is_ajax):
        """ Check if user follows another one """
        mock_is_ajax.response_value = True

        data = {"targetId": self.normal_user2.id}

        response = self.client.post(reverse('toggle_follow_user'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "created")

        response = self.client.post(reverse('toggle_follow_user'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "deleted")


class FanficsOfUserTests(TestCase):

    def setUp(self):
        self.normal_user = CustomUser.objects.create(
            name_surname="name",
            country="AM",
            date_of_birth="2000-07-02",
            email="em@gm.com",
            username='testuser',
            password="12345")

        self.client = Client()
        self.client.force_login(user=self.normal_user)

        self.type = Type.objects.create(name="testType")
        self.fandom = Fandom.objects.create(name="test_fandom",
                                            type=self.type)
        self.fanfic = Fanfic.objects.create(name="Testek fanfic",
                                            author="michaelRuiz",
                                            web="http://web-fanfic.com",
                                            genre1="adv",
                                            complete=True)
        self.character = Character.objects.create(name_surname="test "
                                                               "character",
                                                  fandom=self.fandom)
        FandomFanfic.objects.create(fandom=self.fandom, fanfic=self.fanfic,
                                    is_primary=True)
        CharacterFanfic.objects.create(character=self.character,
                                       fanfic=self.fanfic)

    def test_fanfics_of_user_view_status_code(self):
        """ Test show fanfics of user """
        response = self.client.get(reverse('user_fanfics', kwargs={
            'user_id': self.normal_user.id}))
        self.assertEqual(response.status_code, 200)

    def test_fanfics_of_user_filter(self):
        """ Test show fanfics of user """
        data = {
            'sort_by': 0,
            'genre': 'adv',
            'fandom_id': self.fandom.id,
            'status': 1
        }
        response = self.client.get(reverse('user_fanfics', kwargs={
            'user_id': self.normal_user.id}), data=data)
        self.assertEqual(response.status_code, 200)


class GetBackupUserDataTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(name_surname="Testing user",
                                              username="testuser",
                                              email="test@test",
                                              country="US",
                                              date_of_birth="1997-07-08",
                                              password="A1.aaaaa")

    def test_status_code(self):
        response = self.client.get(reverse('user_backup',
                                           kwargs={'user_id':
                                                       self.user.id}),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
