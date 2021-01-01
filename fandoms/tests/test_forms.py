from django.test import SimpleTestCase

from fandoms.forms import FilterFanficsByFandom


class FilterFanficsByFandomTest(SimpleTestCase):

    def test_valid_form(self):
        """ Validate form """
        data = {'sort_by': 1, 'genre': "adv", "language": 'English',
                'length': 1, "status": 2, "rating": 1, "character_a": 14,
                "character_b": 12}
        form = FilterFanficsByFandom(data)
        self.assertTrue(form.is_valid())
