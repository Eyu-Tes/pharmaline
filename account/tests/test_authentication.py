from django.urls import reverse
from . import BaseTest


class RegisterTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.customer_register_url = reverse('account:register',
                                             kwargs={'user_label': 'customer'})
        self.pharmacy_register_url = reverse('account:register',
                                             kwargs={'user_label': 'pharmacy'})

        self.customer_register_input = {
            'first_name': 'testfname',
            'last_name': 'testlname',
            'phone': '+251900000000',
            'email': 'test@email.com',
            'username': 'newtest',
            'password1': 'testing1234',
            'password2': 'testing1234'
        }

        self.pharmacy_register_input = {
            'pharmacy_name': 'testpname',
            'phone': '+251900000000',
            'location': 'testlocation',
            'email': 'testp@email.com',
            'username': 'newtestp',
            'password1': 'testing1234',
            'password2': 'testing1234'
        }

    def test_customer_register_page(self):
        response = self.client.get(self.customer_register_url)
        self.assertTemplateUsed(response, 'account/user_register.html')
        self.assertContains(response, 'customer')

    def test_pharmacy_register_page_appears_only_for_pharma_admin(self):
        self.client.login(username='test3', password='testing3pass')
        response = self.client.get(self.pharmacy_register_url)
        self.assertTemplateUsed(response, 'account/user_register.html')
        self.assertContains(response, 'pharmacy')
        self.client.login(username='test1', password='testing1pass')
        response = self.client.get(self.pharmacy_register_url)
        self.assertEqual(response.status_code, 404)

    def test_can_register_customer(self):
        response = self.client.post(self.customer_register_url, self.customer_register_input)
        self.assertEqual(response.status_code, 302)

    def test_can_register_pharmacy(self):
        self.client.login(username='test3', password='testing3pass')
        response = self.client.post(self.pharmacy_register_url, self.pharmacy_register_input)
        self.assertEqual(response.status_code, 302)

    def test_empty_email_validation_fails(self):
        register_input = {
            'first_name': 'testfname',
            'last_name': 'testlname',
            'phone': '+251900000000',
            'email': '',
            'username': 'newtest',
            'password1': 'testing1234',
            'password2': 'testing1234'
        }
        response = self.client.post(self.customer_register_url, register_input)
        self.assertEqual(response.status_code, 200)

    def test_existing_email_validation_fails(self):
        register_input = {
            'first_name': 'testfname',
            'last_name': 'testlname',
            'phone': '+251900000000',
            'email': 'test1@email.com',
            'username': 'newtest',
            'password1': 'testing1234',
            'password2': 'testing1234'
        }
        response = self.client.post(self.customer_register_url, register_input)
        self.assertEqual(response.status_code, 200)


class LoginTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.customer_login_url = reverse('account:login',
                                          kwargs={'user_label': 'customer'})
        self.pharmacy_login_url = reverse('account:login',
                                          kwargs={'user_label': 'pharmacy'})
        self.pharma_admin_login_url = reverse('account:login',
                                              kwargs={'user_label': 'pharma_admin'})
        self.wrong_login_url = reverse('account:login',
                                       kwargs={'user_label': 'wrong_label'})

        self.customer_login_input = {
            'username': 'test1',
            'password': 'testing1pass'
        }
        self.pharmacy_login_input = {
            'username': 'test2',
            'password': 'testing2pass',
        }
        self.pharma_admin_login_input = {
            'username': 'test3',
            'password': 'testing3pass',
        }
        self.wrong_user_input = {
            'username': 'testwrong',
            'password': 'test123wrongpass'
        }

    def test_customer_login_page(self):
        response = self.client.get(self.customer_login_url)
        self.assertTemplateUsed(response, 'account/user_login.html')
        self.assertContains(response, 'Customer')

    def test_pharmacy_login_page(self):
        response = self.client.get(self.pharmacy_login_url)
        self.assertTemplateUsed(response, 'account/user_login.html')
        self.assertContains(response, 'Pharmacy')

    def test_pharma_admin_login_page(self):
        response = self.client.get(self.pharma_admin_login_url)
        self.assertTemplateUsed(response, 'account/user_login.html')
        self.assertContains(response, 'Administrator')

    def test_wrong_login_url(self):
        response = self.client.get(self.wrong_user_input)
        self.assertEqual(response.status_code, 404)

    def test_customer_login_correct(self):
        response = self.client.post(self.customer_login_url, self.customer_login_input)
        self.assertEqual(response.status_code, 302)

    def test_pharmacy_login(self):
        response = self.client.post(self.pharmacy_login_url, self.pharmacy_login_input)
        self.assertEqual(response.status_code, 302)

    def test_pharma_admin_login(self):
        response = self.client.post(self.pharma_admin_login_url, self.pharma_admin_login_input)
        self.assertEqual(response.status_code, 302)

    def test_user_login_with_incorrect_credential(self):
        response = self.client.post(self.customer_login_url, self.wrong_user_input)
        self.assertEqual(response.status_code, 200)

    def test_user_login_to_wrong_account(self):
        response = self.client.post(self.customer_login_url, self.pharmacy_login_input)
        self.assertEqual(response.status_code, 200)


# class UpdateAccountTest(BaseTest):
#     def setUp(self):
#         super().setUp()
#         # self.user = authenticate(username='test', password='testing1234')
#         self.update_account_url = reverse('account:profile',
#                                           kwargs={'user_label': 'customer', 'fk': self.user.id})
#         print(self.user)
#         print(self.user.id)
#         print(self.customer)
#
#     def test_can_view_page_correctly(self):
#         response = self.client.get(self.update_account_url)
#         self.assertTemplateUsed(response, 'account/user_profile.html')
#
#     def test_empty_email_validation_fails(self):
#         update_account_input = {
#             'first_name': 'testfname',
#             'last_name': 'testlname',
#             'phone': '+251900000000',
#             'email': '',
#             'username': 'newtest',
#             'password1': 'testing1234',
#             'password2': 'testing1234'
#         }
#         response = self.client.post(self.update_account_url, update_account_input)
#         self.assertEqual(response.status_code, 200)
#
#     def test_existing_email_validation_fails(self):
#         update_account_input = {
#             'first_name': 'testfname',
#             'last_name': 'testlname',
#             'phone': '+251900000000',
#             'email': 'testemail@email.com',
#             'username': 'newtest',
#             'password1': 'testing1234',
#             'password2': 'testing1234'
#         }
#         response = self.client.post(self.update_account_url, update_account_input)
#         self.assertEqual(response.status_code, 200)
