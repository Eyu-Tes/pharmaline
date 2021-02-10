from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Customer, Pharmacy, PharmaAdmin


class BaseTest(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            username='test1',
            email='test1@email.com',
            password='testing1pass',
            # is_active=False
        )

        self.user2 = get_user_model().objects.create_user(
            username='test2',
            email='test2@email.com',
            password='testing2pass'
        )

        self.user3 = get_user_model().objects.create_user(
            username='test3',
            email='test3@email.com',
            password='testing3pass'
        )

        self.customer = Customer.objects.create(
            first_name='testfname',
            last_name='testlname',
            phone='+251900000000',
            user=self.user1
        )

        self.pharmacy = Pharmacy.objects.create(
            pharmacy_name='testpname',
            phone='+251900000000',
            location='testlocation',
            user=self.user2
        )

        self.pharma_admin = PharmaAdmin.objects.create(
            first_name='testafname',
            last_name='testalname',
            phone='+251900000000',
            user=self.user3
        )

        return super().setUp()
