from django.test import SimpleTestCase, TestCase
from common.utils import clean_string
from fanfics.custom_models import FanficWeb as Fanfic
from unittest import mock


class FanficTests(SimpleTestCase):

    ''' Get the site name of url '''

    def setUp(self):
        self.fanfic = Fanfic("url")

    def test_get_correct_site_ficwad(self):
        url = "ficwad.com"
        self.fanfic.url = url
        self.assertEqual(self.fanfic.get_site(), "ficwad.com")

    def test_get_correct_site_avengersfanfiction(self):
        url = "avengersfanfiction.com"
        self.fanfic.url = url
        self.assertEqual(self.fanfic.get_site(),
                         "avengersfanfiction.com")

    def test_get_correct_site_archiveofourown(self):
        url = "archiveofourown.org"
        self.fanfic.url = url
        self.assertEqual(self.fanfic.get_site(), "archiveofourown.org")

    def test_get_incorrect_site(self):
        url = "whatever.org"
        self.fanfic.url = url
        self.assertEqual(self.fanfic.get_site(), None)

    ''' Check if url format is ok '''

    def test_check_url_format_ok(self):
        url = "http://ficwad.com/story/whatever-whatever"
        self.fanfic.url = url
        self.assertEqual(self.fanfic.check_url_format(), True)

    def test_check_url_format_not_ok(self):
        url = "http://sdfsdf.com/whatever-whatever"
        self.fanfic.url = url
        self.assertEqual(self.fanfic.check_url_format(), False)

    ''' Check if online '''
    @mock.patch('requests.get')
    def test_check_if_online_true(self, mock_request):
        mock_request.return_value.status_code = 200
        url = "valid-url"
        self.fanfic.url = url
        self.assertEqual(self.fanfic.check_if_online(), True)

    @mock.patch('requests.get')
    def test_check_if_online_false(self, mock_request):
        mock_request.return_value.status_code = 404
        url = "url-not-valid"
        self.fanfic.url = url
        self.assertEqual(self.fanfic.check_if_online(), False)


''' These next tests are real ones, they need internet connection '''


class FicWadTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super(FicWadTests, cls).setUpClass()
        url = "https://ficwad.com/story/204190"
        cls.fanfic_ficwad = Fanfic(url)
        cls.fanfic_ficwad.set_appropiate_scraper()
        cls.fanfic_ficwad.load_page_html()

    def test_get_title_and_author_ficwad(self):
        title, author = self.fanfic_ficwad.get_title_and_author()
        self.assertEqual(title, "My Dirty Little Secret")
        self.assertEqual(author, "BleedingValentine")

    def test_get_fandom_and_media_type_ficwad(self):
        fandom, media_type = self.fanfic_ficwad.get_fandom_and_media_type()
        self.assertEqual(fandom, "My Chemical Romance")
        self.assertEqual(media_type, "other")

    def test_get_language_ficwad(self):
        language = self.fanfic_ficwad.get_language()
        self.assertEqual(language, None)

    def test_get_genres_ficwad(self):
        genres = self.fanfic_ficwad.get_genres()
        self.assertEqual(genres, ["drama", "humor", "romance"])

    def test_get_status_ficwad(self):
        status = self.fanfic_ficwad.get_status()
        self.assertFalse(status)

    def test_get_rating_ficwad(self):
        rating = self.fanfic_ficwad.get_rating()
        self.assertEqual(rating, "T")


class AvengersFanfictionTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super(AvengersFanfictionTests, cls).setUpClass()
        url = "http://www.avengersfanfiction.com/Story/86623/The-silvers-tears"
        cls.fanfic_avengers = Fanfic(url)
        cls.fanfic_avengers.set_appropiate_scraper()
        cls.fanfic_avengers.load_page_html()

    def test_get_title_and_author_avengersfanfiction(self):
        title, author = self.fanfic_avengers.get_title_and_author()
        self.assertEqual(title, "The silver's tears")
        self.assertEqual(author, "Lokinada")


class ArchiveOfOurOwnTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super(ArchiveOfOurOwnTests, cls).setUpClass()
        url = "https://archiveofourown.org/works/8109805"
        cls.fanfic = Fanfic(url)
        cls.fanfic.set_appropiate_scraper()
        cls.fanfic.load_page_html()

    def test_get_title_and_author_archiveofourown(self):
        title, author = self.fanfic.get_title_and_author()
        self.assertEqual(title, "WIP Amnesty: Stranger Things Have Happened")
        self.assertEqual(author, "aimmyarrowshigh")

    def test_get_fandom_and_media_type_archiveofourown(self):
        fandom, media_type = self.fanfic.get_fandom_and_media_type()
        self.assertEqual(fandom, "Mediator")
        self.assertEqual(media_type, "books")
