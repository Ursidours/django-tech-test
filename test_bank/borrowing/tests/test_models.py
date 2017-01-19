from test_plus.test import TestCase
from ..models import BorrowerProfile, Business, Loan
from .factories import BorrowerProfileFactory, BusinessFactory, LoanFactory
from test_bank.users.tests.factories import UserFactory


class TestBorrowerProfile(TestCase):

    def setUp(self):
        UserFactory.reset_sequence()
        self.borrower = BorrowerProfileFactory()

    def test__str__(self):
        self.assertEqual(
            self.borrower.__str__(),
            'profile of user-0'
        )


class TestBusiness(TestCase):
    def setUp(self):
        UserFactory.reset_sequence()
        self.business = BusinessFactory()

    def test__str__(self):
        self.assertEqual(
            self.business.__str__(),
            'Test Business -- 01234567'
        )


class TestLoan(TestCase):
    def setUp(self):
        UserFactory.reset_sequence()
        self.loan = LoanFactory()

    def test__str__(self):
        self.assertEqual(
            self.loan.__str__(),
            'GBP 20000 for Test Business -- 01234567'
        )
