from . import BaseTest


class CustomerModelTest(BaseTest):
    def test_string_representation(self):
        self.assertEqual(self.customer.__str__(), self.customer.full_name)


class PharmacyModelTest(BaseTest):
    def test_string_representation(self):
        self.assertEqual(self.pharmacy.__str__(), self.pharmacy.pharmacy_name)


class PharmaAdminModelTest(BaseTest):
    def test_string_representation(self):
        self.assertEqual(self.pharma_admin.__str__(), self.pharma_admin.full_name)
