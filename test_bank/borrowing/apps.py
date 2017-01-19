# -*- coding: utf-8 -*-

from django.apps import AppConfig


class BorrowingConfig(AppConfig):
    name = 'test_bank.borrowing'
    verbose_name = "Borrowing"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
