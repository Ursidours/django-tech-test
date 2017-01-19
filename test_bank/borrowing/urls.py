# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.home_view,
        name='home'
    ),
    url(
        regex=r'^activate/$',
        view=views.BorrowerCreateView.as_view(),
        name='activate_account'
    ),
    url(
        regex=r'^new-business/$',
        view=views.BusinessCreateView.as_view(),
        name='create_business'
    ),
    url(
        regex=r'^update-business/(?P<pk>[\df]+)/$',
        view=views.BusinessUpdateView.as_view(),
        name='update_business'
    ),
    url(
        regex=r'^delete-business/(?P<pk>[\d]+)/$',
        view=views.delete_business,
        name='delete_business'
    ),
    url(
        regex=r'^new-loan/$',
        view=views.LoanCreateView.as_view(),
        name='create_loan'
    ),
    url(
        regex=r'^loan-detail/(?P<pk>[\d]+)/$',
        view=views.LoanDetailView.as_view(),
        name='loan_detail'
    ),
    url(
        regex=r'^cancel-loan/(?P<pk>[\d]+)/$',
        view=views.cancel_loan_request,
        name='cancel_loan'
    ),
    url(
        regex=r'^verify-phone/$',
        view=views.verify_phone,
        name='verify_phone'
    ),
]
