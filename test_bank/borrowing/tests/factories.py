import factory
from ...users.tests.factories import UserFactory
from decimal import Decimal


class BorrowerProfileFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    phone_number = "+447123567890"
    has_signed = True
    is_verified = True

    class Meta:
        model = 'borrowing.BorrowerProfile'


class BusinessFactory(factory.django.DjangoModelFactory):
    owner = factory.SubFactory(BorrowerProfileFactory)
    name = "Test Business"
    address = "42 test street, London"
    company_number = '01234567'
    sector = 'R'

    class Meta:
        model = 'borrowing.Business'


class LoanFactory(factory.django.DjangoModelFactory):
    borrower = factory.SubFactory(BorrowerProfileFactory)
    business = factory.SubFactory(BusinessFactory)
    amount = Decimal("20000")
    currency = "GBP"
    reason = "Need to test"
    duration = 365
    status = 0
    interest_rate = Decimal('0.05000')

    class Meta:
        model = 'borrowing.Loan'