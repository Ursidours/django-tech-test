# -*- coding: utf-8 -*-

from django.db.models import (
    Model, ForeignKey, CharField, BooleanField, DecimalField,
    OneToOneField, DateTimeField, PositiveSmallIntegerField,
)
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator


class BorrowerProfile(Model):
    """
    Profile of a borrower, linked one-to-one with User
    Requires a valid phone number and the consent with the terms
    and conditions
    """
    user = OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    phone_number = PhoneNumberField(blank=True)
    is_verified = BooleanField(default=False)
    has_signed = BooleanField(
        verbose_name=_(
            "By clicking this, you accept our terms and conditions.\n"
            "It is your responsibility to repay any loan, or face a large variety"
            " of very unpleasant consequences."
        ),
        default=False
    )

    def __str__(self):
        return "profile of {0}".format(self.user.username)


class Business(Model):
    """
    A business belonging to a borrower, with a name, address and
    activity sector
    """

    company_number_validator = RegexValidator(
        regex=r'\d{8}',
        message=_("Your company number should be 8 digit long.")
    )
    owner = ForeignKey(BorrowerProfile)
    name = CharField(max_length=64)
    address = CharField(max_length=128)
    company_number = CharField(max_length=8, validators=[company_number_validator, ])
    sector = CharField(
        max_length=1,
        choices=(('R', 'Retail'), ('P', 'Professional Services'),
                 ('F', 'Food & Drink'), ('E', 'Entertainment'),)
    )
    created_at = DateTimeField(default=timezone.now, blank=True, null=True)
    validated_at = DateTimeField(default=timezone.now, blank=True, null=True)

    def __str__(self):
        return "{0} -- {1}".format(self.name, self.company_number)

    class Meta:
        verbose_name_plural = "businesses"


class Loan(Model):
    """
    A loan, defined by amount, currency, reason, duration and interest rate
    It relates to a business and a borrower
    """
    amount = DecimalField(
        max_digits=9, decimal_places=2,
        validators=[MinValueValidator(10000), MaxValueValidator(100000)],
        verbose_name=_("The amount in GBP requested for your loan"),
        help_text=_("It should be between 10k and 100k"),
    )

    borrower = ForeignKey(BorrowerProfile)

    business = ForeignKey(Business)

    currency = CharField(max_length=3, default='GBP')

    reason = CharField(
        max_length=256,
        help_text=_("Please state your reason for applying to this loan"),
        )

    duration = PositiveSmallIntegerField(
        validators=[MaxValueValidator(10000)],
        verbose_name=_(
            "Loan duration in days"
        ),
    )

    interest_rate = DecimalField(
        max_digits=6, decimal_places=5, validators=[MinValueValidator(0)],
        verbose_name=_("AER interest rate"),
    )

    created_at = DateTimeField(default=timezone.now, blank=True, null=True)

    modified_at = DateTimeField(default=timezone.now, blank=True, null=True)

    status = PositiveSmallIntegerField(
        default=0,
        choices=(
            (0, 'Pending'), (1, 'Approved'),
            (2, 'Processed'), (3, 'Rejected'),
            (4, 'Cancelled'), (5, 'Repaid'),
        )
    )

    def __str__(self):
        return "{1} {0} for {2}".format(self.amount, self.currency, self.business)
