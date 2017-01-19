# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import BorrowerProfile, Business, Loan


class BorrowerProfileAdmin(admin.ModelAdmin):
    pass


class BusinessAdmin(admin.ModelAdmin):
    pass


class LoanAdmin(admin.ModelAdmin):
    pass


admin.site.register(BorrowerProfile, BorrowerProfileAdmin)
admin.site.register(Business, BusinessAdmin)
admin.site.register(Loan, LoanAdmin)
