from django.test import TestCase

from chapters.forms.admin_forms import ChapterAddForm
from common.models import Type, Fandom, Fanfic, Chapter


class ChapterAddFormTest(TestCase):

    def setUp(self):
        self.type = Type.objects.create(name="test_type")
        self.fandom = Fandom.objects.create(name="test_fandom", type=self.type)
        self.fanfic = Fanfic.objects.create(name="Testek fanfic",
                                            author="michaelRuiz",
                                            web="http://web-fanfic.com",
                                            genre1="adv",
                                            complete=True)
        self.chapter = Chapter.objects.create(title="test chapter",
                                              num_chapter=1,
                                              url_chapter="whatever2.com",
                                              fanfic=self.fanfic)

    def test_valid_form(self):
        """ Create chapter form """
        data = {'title': "Testing test", 'num_chapter': 2,
                'url_chapter': 'whatever.com', 'fanfic': self.fanfic.id}
        form = ChapterAddForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_num_chapter(self):
        """ Create chapter invalid num chapter """
        data = {'title': "Testing test", 'num_chapter': 1,
                'url_chapter': 'whatever.com', 'fanfic': self.fanfic.id}
        form = ChapterAddForm(data=data)
        self.assertFalse(form.is_valid())


