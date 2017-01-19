from test_plus.test import TestCase
from ..forms import BorrowerProfileForm, UserUpdateForm, UserBorrowerForm, LoanForm
from ..helper_functions import get_verification_code
from test_bank.borrowing.tests.factories import BusinessFactory,\
    BorrowerProfileFactory
from test_bank.borrowing.helper_functions import calculate_interest_rate
from decimal import Decimal


class TestBorrowerProfileForm(TestCase):

    def setUp(self):
        self.user = self.make_user()
        self.valid_data = {
            'phone_number': '+447123456789',
            'code': get_verification_code("+447123456789"),
            'has_signed': 'on',
        }

    def test_all_valid(self):
        """ self.valid_data should yield a valid form """
        form = BorrowerProfileForm(data=self.valid_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_no_phonenumber(self):
        """
        No phone number -- form.errors should contain a single error called 'phone number'
        phonenumber already provides test on PhoneNumberField
        """
        data = self.valid_data
        data.pop('phone_number')
        form = BorrowerProfileForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('phone_number' in form.errors)

    def test_invalid_phonenumber(self):
        """
        No phone number -- form.errors should contain a single error called 'phone number'
        phonenumber already provides test on PhoneNumberField
        """
        data = self.valid_data
        data['phone_number'] = "+442345"
        form = BorrowerProfileForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('phone_number' in form.errors)

    def test_already_taken_phonenumber(self):
        """
        No phone number -- form.errors should contain a single error called 'phone number'
        phonenumber already provides test on PhoneNumberField
        """
        BorrowerProfileFactory(phone_number="+447123456789")
        form = BorrowerProfileForm(data=self.valid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('phone_number' in form.errors)

    def test_no_code(self):
        """ verification code not provided -> 'code' errors"""
        data = self.valid_data
        data.pop('code')
        form = BorrowerProfileForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('code' in form.errors)

    def test_incorrect_format_code(self):
        """ verification code is not 5 character long -> 'code' error """
        data = self.valid_data
        data['code'] = "ABCD"
        form = BorrowerProfileForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('code' in form.errors)

    def test_invalid_code(self):
        """ verification code is the correct format but invalid -> 1 non field error"""
        data = self.valid_data
        data['code'] = "ABCDI"
        form = BorrowerProfileForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('__all__' in form.errors)

    def test_not_signed(self):
        data = self.valid_data
        data.pop('has_signed')
        form = BorrowerProfileForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('has_signed' in form.errors)


class TestUserUpdateForm(TestCase):

    def setUp(self):
        self.user = self.make_user()
        self.valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
        }

    def test_valid(self):
        """ tests valid form """
        form = UserUpdateForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_no_first_name(self):
        """ No first name -- form.errors should contain a single error called 'first_name' """
        data = self.valid_data
        data.pop('first_name')
        form = UserUpdateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('first_name' in form.errors)

    def test_no_last_name(self):
        """ No last name -- form.errors should contain a single error called 'first_name' """
        data = self.valid_data
        data.pop('last_name')
        form = UserUpdateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('last_name' in form.errors)


class TestUserBorrowerForm(TestCase):
    """ Test Case for the Form combining UserUpdateForm and TestBorrowerProfileForm"""
    def test_validity(self):
        user = self.make_user()
        valid_data = {
            'phone_number': '+447123456789',
            'code': get_verification_code("+447123456789"),
            'has_signed': 'on',
            'first_name': 'John',
            'last_name': 'Doe',
        }
        form = UserBorrowerForm(data=valid_data, user=user)
        self.assertTrue(form.is_valid())


class TestLoanForm(TestCase):
    """ Test Case for the Loan Creation Form """
    def setUp(self):
        self.business = BusinessFactory()
        self.valid_data = {
            'business': self.business.pk,
            'reason': "Test",
            'duration': 5,
            'interest_rate': '0.05',
            'amount': 15000
        }

    def test_validity(self):
        """ checks form validity with valid input """
        form = LoanForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_no_business(self):
        """ check rejection of form without business """
        data = self.valid_data
        data.pop('business')
        form = LoanForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('business' in form.errors)

    def test_invalid_no_reason(self):
        """ reject forms without a stated reason """
        data = self.valid_data
        data.pop('reason')
        form = LoanForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('reason' in form.errors)

    def test_invalid_no_interest_rate(self):
        """ reject forms with no interest rate """
        data = self.valid_data
        data.pop('interest_rate')
        form = LoanForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('interest_rate' in form.errors)

    def test_invalid_mismatched_interest_rate(self):
        """
        reject forms for which the interest rate does not match what is
        returned by the helper_functon calculate_interest_rate
        """
        data = self.valid_data
        data['interest_rate'] = Decimal('0.1') + calculate_interest_rate(
            amount=data['amount'],
            duration=data['duration']
        )
        form = LoanForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('__all__' in form.errors)

    def test_invalid_no_amount(self):
        """ reject forms with no amount """
        data = self.valid_data
        data.pop('interest_rate')
        form = LoanForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('interest_rate' in form.errors)

    def test_invalid_too_large_amount(self):
        """ reject forms with an amount above 100k """
        data = self.valid_data
        data['amount'] = 100000.01
        form = LoanForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('amount' in form.errors)

    def test_invalid_too_small_amount(self):
        """ reject forms with an amount < 10k """
        data = self.valid_data
        data['amount'] = 9999.99
        form = LoanForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('amount' in form.errors)

    def test_invalid_strange_duration(self):
        """ reject forms with a non-integer duration """
        data = self.valid_data
        data['duration'] = 9999.99
        form = LoanForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('duration' in form.errors)

    def test_invalid_no_duration(self):
        """ reject forms with a non-integer duration """
        data = self.valid_data
        data.pop('duration')
        form = LoanForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('duration' in form.errors)
