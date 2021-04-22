from django.apps import apps
from django.test import SimpleTestCase
from account.apps import AccountConfig


class AccountConfigTest(SimpleTestCase):
    def test_apps(self):
        self.assertEqual(AccountConfig.name, 'account')
