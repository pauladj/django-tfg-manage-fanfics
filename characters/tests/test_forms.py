from django.test import TestCase

from characters.forms.admin_forms import CharacterAddForm
from common.models import Type, Fandom


class CharacterAddFormTest(TestCase):

    def setUp(self):
        self.type = Type.objects.create(name="test_type")
        self.fandom = Fandom.objects.create(name="test_fandom", type=self.type)

    def test_valid_form(self):
        """ Create character form """
        data = {'name_surname': "Testing character", 'fandom': self.fandom.id}
        form = CharacterAddForm(data)
        self.assertTrue(form.is_valid())
