# -*- coding: utf-8 -*-

from hashlib import sha256
from django.conf import settings
from decimal import Decimal
from builtins import NotImplementedError


def calculate_interest_rate(amount, duration, *args):
    """
    calculates the interest rate based on the characteristics of
    the loan: amount, duration, etc, as well as other parameters
    yet to be determined (interbank rate, trust in borrower, etc)
    (Not yet implemented -> returns always 0.05)
    """
    return Decimal('0.05000')


def get_verification_code(phone_number):
    """
    calculates in a deterministic way the PIN number by taking the few first
    characters of the sha256 hash of the phone_number appended to a secret key
    saves the need to a db call with some sort of PhoneActivationLink
    """
    to_encode = settings.PHONE_SECRET_KEY + str(phone_number)
    hashed_value = sha256(to_encode.encode('utf-8')).hexdigest()
    list_of_int = [int(x, 16) + int(y, 16) for x, y in zip(hashed_value[0:5], hashed_value[5:10])]
    # alphabet A-Z without the I plus the numbers to make 32 choices
    characters = 'ABCDEFGHJKLMNOPQRSTUVWXYZ1234567'
    code = ''.join([characters[i] for i in list_of_int])
    return code


def send_code_to_user(phone_number):
    """
    sends the validation code to the user, in debug displays to the console
    in production would use twilio
    """
    if settings.DEBUG:
        print(
            "SMS sent to {0}\nYour PIN number is {1}".format(
                phone_number, get_verification_code(phone_number)
            )
        )
    else:
        raise NotImplementedError
