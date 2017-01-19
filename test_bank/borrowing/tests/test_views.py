from django.test import RequestFactory
from test_plus.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from test_bank.users.tests.factories import UserFactory
from .factories import BorrowerProfileFactory, BusinessFactory, LoanFactory
from decimal import Decimal

from ..views import (
    home_view,
    BorrowerCreateView,
    BusinessCreateView,
    BusinessUpdateView,
    LoanCreateView,
    LoanDetailView,
    cancel_loan_request,
    verify_phone,
)

from test_bank.borrowing.helper_functions import get_verification_code
from test_bank.borrowing.models import BorrowerProfile, Business, Loan


class BaseBorrowingTestCase(TestCase):

    def setUp(self):
        """
        creates a new user 'user-0' and attach it to a request
        """
        UserFactory.reset_sequence()
        self.user = UserFactory()
        self.client = Client()
        self.client.login(username=self.user.username, password='password')

    def run_test_login_required(self):
        """
        makes sure that if a user is not logged in,
        she is redirected
        """
        response = Client().get(self.url)
        self.assertEqual(
            response.status_code, 302
        )

    def run_test_borrower_required(self):
        """
        checks if a user which has not a completed borrower profile is redirected
        to borrowing:home
        """
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response, reverse("borrowing:home"), status_code=302, target_status_code=200
        )


class TestHome(BaseBorrowingTestCase):
    """ Test case for the home page of the borrower section """

    def setUp(self):
        super().setUp()
        self.url = reverse('borrowing:home')

    def test_login_required(self):
        self.run_test_login_required()

    def test_new_user_should_apply_to_borrower(self):
        """ makes sure a logged-in user with no profile has a link to become borrower"""
        response = self.client.get(self.url)
        self.assertContains(
            response,
            'href="{0}"'.format(reverse("borrowing:activate_account")),
            status_code=200,
        )

    def test_borrower_no_business_links(self):
        """
        checks a borrower with no business has a link to
        create a new business but no link to create a loan
        """
        borrower = BorrowerProfileFactory(user=self.user)
        response = self.client.get(self.url)
        self.assertContains(
            response, 'href="{0}"'.format(reverse("borrowing:create_business")),
            status_code=200
        )
        self.assertNotIn('href="{0}"'.format(reverse("borrowing:create_loan")), str(response.content))

    def test_borrower_with_business(self):
        """
        checks a borrower with businesses has a link to create new loans and
        have all businesses and loans listed
        """
        borrower = BorrowerProfileFactory(user=self.user)
        business1 = BusinessFactory(owner=borrower)
        loan1 = LoanFactory(business=business1, borrower=borrower)
        loan2 = LoanFactory(business=business1, borrower=borrower)
        business2 = BusinessFactory(owner=borrower)

        response = self.client.get(self.url)
        self.assertContains(
            response,
            'href="{0}"'.format(reverse("borrowing:create_business")),
            status_code=200,
        )
        self.assertContains(
            response,
            'href="{0}"'.format(reverse("borrowing:create_loan"))
        )
        # Link to update business without loans; no link for those with a loan
        self.assertContains(
            response,
            'href="{0}"'.format(reverse("borrowing:update_business", kwargs={'pk': 2})),
        )
        self.assertNotContains(
            response,
            'href="{0}"'.format(reverse("borrowing:update_business", kwargs={'pk': 1})),
        )
        # Link to see the details of loan 2
        self.assertContains(
            response,
            'href="{0}"'.format(reverse("borrowing:loan_detail", kwargs={'pk': 2})),
        )


#  ------------------------------------------------
#                BORROWER VIEWS
#  ------------------------------------------------


class TestBorrowerCreateView(BaseBorrowingTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('borrowing:activate_account')

    def test_login_required(self):
        self.run_test_login_required()

    def test_redirect_home_if_already_borrower(self):
        """
        once created, this profile can no longer be modified
        -> redirect to borrowing:home
        """
        borrower = BorrowerProfileFactory(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_success_url(self):
        """" should redirect to the page to setup a new business """
        self.assertEqual(
            BorrowerCreateView().get_success_url(),
            reverse('borrowing:create_business')
        )

    def test_creation(self):
        """
        checks a new borrower profile has been created upon submission of
        valid data (test with invalid data are in test.forms)
        """
        data = {
            'phone_number': "+447123567890",
            'code': get_verification_code("+447123567890"),
            'has_signed': 'on',
            'first_name': 'Jane',
            'last_name': 'Doe',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Jane')
        borrower = BorrowerProfile.objects.get(user=self.user)
        self.assertEqual(borrower.phone_number, "+447123567890")


#  ------------------------------------------------
#                BUSINESS VIEWS
#  ------------------------------------------------


class TestBusinessCreateView(BaseBorrowingTestCase):
    """ Test Case for the CBV Business Create View """

    def setUp(self):
        super().setUp()
        self.view = BusinessCreateView.as_view()
        self.url = reverse("borrowing:create_business")

    def test_login_required(self):
        self.run_test_login_required()

    def test_redirect_home_if_not_borrower(self):
        self.run_test_borrower_required()

    def test_get_success_url(self):
        """" upon success, redirect to borrowing:home"""
        self.assertEqual(
            BusinessCreateView(object=BusinessFactory()).get_success_url(),
            reverse('borrowing:home')
        )

    def test_creation(self):
        """
        checks a new business profile has been created upon submission of
        valid data
        """
        borrower = BorrowerProfileFactory(user=self.user)
        data = {
            "name": "Test Business",
            "address": "42 test street, London",
            "company_number": '01234567',
            "sector": "R",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        business = borrower.business_set.first()
        self.assertEqual(business.name, 'Test Business')


class TestBusinessUpdateView(BaseBorrowingTestCase):

    def setUp(self):
        super().setUp()
        self.borrower = BorrowerProfileFactory(user=self.user)
        self.business = BusinessFactory(owner=self.borrower)
        self.url = reverse("borrowing:update_business", kwargs={"pk": self.business.pk})

    def test_login_required(self):
        self.run_test_login_required()

    def test_redirect_home_if_not_borrower(self):
        """ makes sure access is restricted to approved borrower """
        c = Client()
        new_user = UserFactory()
        c.login(username=new_user.username, password="password")
        response = c.post(self.url, {}, follow=True)
        self.assertRedirects(
            response, reverse('borrowing:home'),
            status_code=302,
            target_status_code=200
        )

    def test_get_success_url(self):
        """" should redirect to the page to setup a new business """
        """" upon success, redirect to borrowing:home"""
        self.assertEqual(
            BusinessUpdateView(object=self.business).get_success_url(),
            reverse('borrowing:home')
        )

    def test_successful_update(self):
        """
        posts valid data and checks the Business is updated accordingly
        """
        data = {
            "name": "Edited Business",
            "address": "42 edited street, London",
            "company_number": '76543210',
            "sector": "R",
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('borrowing:home'), status_code=302, target_status_code=200)
        # We refresh the object from db and check it has been updated
        business = Business.objects.get(pk=1)
        self.assertEqual(business.name, "Edited Business")

    def test_denied_update_to_others_businesses(self):
        """
        The user should be denied access to businesses belonging to other
        users
        """
        other_business = BusinessFactory()
        self.url = reverse("borrowing:update_business", kwargs={"pk": other_business.pk})
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 404)


class TestBusinessDeleteView(BaseBorrowingTestCase):

    def setUp(self):
        super().setUp()
        self.borrower = BorrowerProfileFactory(user=self.user)
        self.business = BusinessFactory(owner=self.borrower)
        self.url = reverse('borrowing:delete_business', kwargs={"pk": self.business.pk})

    def test_login_required(self):
        self.run_test_login_required()

    def test_redirect_home_if_not_borrower(self):
        """ makes sure access is restricted to approved borrower """
        c = Client()
        new_user = UserFactory()
        c.login(username=new_user.username, password="password")
        response = c.post(self.url, {}, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_successful_update(self):
        """
        posts valid data and checks the Business has been destroyed as expected
        """
        response = self.client.post(self.url, {})
        self.assertRedirects(response, reverse('borrowing:home'), status_code=302, target_status_code=200)
        with self.assertRaises(Business.DoesNotExist):
            Business.objects.get(pk=1)

    def test_deny_deletion_to_others_businesses(self):
        """
        The user should be denied access to businesses belonging to other
        users
        """
        other_business = BusinessFactory()
        self.url = reverse("borrowing:delete_business", kwargs={"pk": other_business.pk})
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 404)


#  ------------------------------------------------
#                LOAN VIEWS
#  ------------------------------------------------


class TestLoanCreateView(BaseBorrowingTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('borrowing:create_loan')

    def test_login_required(self):
        self.run_test_login_required()

    def test_borrower_required(self):
        self.run_test_borrower_required()

    def test_get_success_url(self):
        """" should redirect to borrowing:home """
        self.assertEqual(
            LoanCreateView(object=LoanFactory()).get_success_url(),
            reverse('borrowing:home')
        )

    def test_legit_user_valid_data(self):
        """
        checks a new loan is created for a legit user inputting
        correct data
        """
        borrower = BorrowerProfileFactory(user=self.user)
        business = BusinessFactory(owner=borrower)
        data = {
            'business': business.pk,
            'reason': "Test",
            'duration': 5,
            'interest_rate': '0.05',
            'amount': 15000
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        new_loan = Loan.objects.last()
        self.assertEqual(new_loan.interest_rate, Decimal('0.05'))


class TestLoanDetailView(BaseBorrowingTestCase):
    """
    Test Case for Loan Details
    """
    def setUp(self):
        super().setUp()
        borrower = BorrowerProfileFactory(user=self.user)
        self.loan = LoanFactory(borrower=borrower)
        self.url = reverse("borrowing:loan_detail", kwargs={"pk": self.loan.pk})

    def test_login_required(self):
        self.run_test_login_required()

    def test_borrower_required(self):
        """
        404 if no valid borrower account
        """
        c = Client()
        new_user = UserFactory()
        c.login(username=new_user.username, password="password")
        response = c.get(self.url, {}, follow=True)
        self.assertRedirects(
            response, reverse("borrowing:home"), status_code=302, target_status_code=200
        )

    def test_legit_access(self):
        """
        checks the rightful user can access the page
        """
        response = self.client.get(self.url)
        self.assertContains(
            response,
            "Loan of 20000.00 GBP",
            status_code=200
        )

    def test_deny_access_to_others_loans(self):
        """
        raise 404 if attempting access to other users' loan
        """
        loan2 = LoanFactory()
        url = reverse("borrowing:loan_detail", kwargs={"pk": loan2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TestLoanCancelView(BaseBorrowingTestCase):

    def setUp(self):
        super().setUp()
        borrower = BorrowerProfileFactory(user=self.user)
        self.loan = LoanFactory(borrower=borrower)
        self.url = reverse("borrowing:cancel_loan", kwargs={"pk": self.loan.pk})

    def test_login_required(self):
        self.run_test_login_required()

    def test_borrower_required(self):
        """
        if the user doesn't have a valid borrower profile
        redirects her to borrowing:home
        """
        c = Client()
        c.login()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

    def test_deny_cancellation_others_loan(self):
        """
        Accessing another loan should yield error 404
        """
        loan2 = LoanFactory()
        url = reverse("borrowing:cancel_loan", kwargs={"pk": loan2.pk})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 404)

    def test_cancelling_valid_loan(self):
        """
        A cancelled loan has status == 4
        """
        self.client.post(self.url, {})
        loan = Loan.objects.get(pk=1)
        self.assertEqual(loan.status, 4)


#  ------------------------------------------------
#                PHONE VIEWS
#  ------------------------------------------------


class TestPhoneView(BaseBorrowingTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("borrowing:verify_phone")

    def test_login_required(self):
        self.run_test_login_required()

    def test_valid_phone_number(self):
        """
        A valid phone number should return a response with status code 200
        """
        with self.settings(DEBUG=True):
            response = self.client.post(self.url, {'phone_number': '+447123456789'})
            self.assertEqual(response.status_code, 200)

    def test_invalid_phone_number(self):
        """
        An invalid phone number should return a response with status code 400
        """
        response = self.client.post(self.url, {'phone_number': '+447189'})
        self.assertEqual(response.status_code, 400)
