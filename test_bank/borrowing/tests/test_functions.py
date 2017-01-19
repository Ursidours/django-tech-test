from test_plus.test import TestCase
import random
from collections import Counter

from ..helper_functions import get_verification_code


def generate_phone_number():
    """ generates a valid UK phone number at random """
    return '+44' + ''.join([str(n) for n in random.sample(range(10), 9)])

    
class TestGetVerificationCode(TestCase):
    """
    test case for the function generating the phone verification code
    the output should show high variability (chances of collisions ~ n * 1 over 30 millions
    -> enough to warrant random testing here) and always be 5 character long
    """
    
    def test_100_numbers(self):
        # List comprehension to generate many phone numbers 
        # we convert to set to guarantee uniqueness
        numbers = set([generate_phone_number() for _ in range(100)])
        codes = [get_verification_code(number) for number in numbers]
        self.assertTrue(all(len(code) == 5 for code in codes))
        self.assertTrue(all(value == 1 for value in Counter(codes).values()))
