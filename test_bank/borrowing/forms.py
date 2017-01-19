# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import RegexField
from phonenumber_field.formfields import PhoneNumberField

from test_bank.users.models import User
from .models import BorrowerProfile

from .helper_functions import send_code_to_user, get_verification_code
from test_bank.borrowing.helper_functions import calculate_interest_rate
from test_bank.borrowing.models import Loan


class VeriFyPhoneForm(forms.Form):
    """
    Form validating the phone number provided and if valid
    sending the code to the user
    """
    phone_number = PhoneNumberField(required=True)

    def process(self):
        phone_number = self.cleaned_data.get('phone_number')
        send_code_to_user(phone_number=phone_number)


class UserUpdateForm(forms.ModelForm):
    """
    Form updating the first and last names of a user
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class BorrowerProfileForm(forms.ModelForm):
    """
    Form creating a borrower Profile, in charge also of verifying
    the phone number by checking a verification code sent by SMS
    """
    code = RegexField(
        label=_("Verification code for your number"),
        regex=r'[A-Z0-9]{5}',
        error_message=_("Please enter the 5 character of the code sent to your number by text")
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["has_signed"].required = True
        self.fields["phone_number"].required = True

    def save(self):
        # We attach the related user to the profile
        instance = super().save(commit=False)
        instance.user = self.user
        instance.save()
        return instance

    def clean_phone_number(self):
        """no other user should have already validated this number"""
        phone_number = self.cleaned_data['phone_number']
        if BorrowerProfile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(_("Another user has already registered this number."))
        return phone_number

    def clean(self):
        # The code must correspond to what has been sent by SMS
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        phone_number = cleaned_data.get('phone_number')
        if code and phone_number and code != get_verification_code(phone_number):
            raise forms.ValidationError(_(
                "The validation code you entered is not correct."
                "Please check your number and click \"Verify my number\" again."
            ))

    class Meta:
        model = BorrowerProfile
        fields = ['phone_number', 'has_signed']


class UserBorrowerForm:

    def __init__(self, user, borrower=None, data=None, *args, **kwargs):
        self.borrower_form = BorrowerProfileForm(instance=borrower, user=user, data=data)
        self.user_form = UserUpdateForm(instance=user, data=data)

    def is_valid(self):
        return self.borrower_form.is_valid() and self.user_form.is_valid()

    def save(self):
        self.user_form.save()
        self.borrower_form.save()


class LoanForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        duration = cleaned_data.get('duration')
        interest_rate = cleaned_data.get('interest_rate')
        non_valid = (amount and duration and interest_rate and
                     interest_rate != calculate_interest_rate(amount, duration))
        if non_valid:
            raise forms.ValidationError("There was a problem calculating your interest rate.")

    class Meta:
        model = Loan
        fields = ['amount', 'business', 'reason', 'duration', 'interest_rate']
