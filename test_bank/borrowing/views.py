# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.http import Http404
from django.core.urlresolvers import reverse
from django.views.generic import (
    DetailView,
    UpdateView,
    CreateView,
    FormView
)
from django.http.response import (
    HttpResponseNotAllowed,
    HttpResponseRedirect,
    HttpResponseBadRequest,
    JsonResponse,
)

from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.urls.base import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils import timezone
from django.db.models import Count

from .forms import UserBorrowerForm, VeriFyPhoneForm, LoanForm
from .models import BorrowerProfile, Business, Loan


@login_required
def verify_phone(request):
    """
    returns status 200 if the verification number was sent to the user,
    else returns 400
    """
    if not request.method == "POST":
        return HttpResponseNotAllowed(['POST'])
    form = VeriFyPhoneForm(request.POST)
    if form.is_valid():
        form.process()
        return JsonResponse({})
    else:
        return HttpResponseBadRequest(_("Your phone number is not valid. Try the format +447xxxxxxxxx"))


#  ----------------------------------------------------
#        Borrower Profile Views
#  ----------------------------------------------------


@login_required
def home_view(request):
    """
    returns the home view of the borrowing section. Gives a summary of
    whether the borrower profile account has been properly set up and a
    summary of the business registered and loans subscribed
    """
    try:
        borrower = BorrowerProfile.objects.get(user=request.user)
        businesses = Business.objects.filter(owner=borrower).annotate(loan_nb=Count('loan', distinct=True))
        loans = borrower.loan_set.all()
    except BorrowerProfile.DoesNotExist:
        borrower, businesses, loans = None, None, None
    return render(
        request, "borrowing/home.html",
        {"borrower": borrower, 'businesses': businesses, 'loans': loans}
    )


class BorrowerCreateView(LoginRequiredMixin, FormView):
    """
    CBV view to activate the user's borrower profile. Instantiate a UserBorrowerForm,
    an hybrid form to update both first_name and last_name and the profile info at
    the same time.
    """
    template_name = 'borrowing/account_activation.html'
    form_class = UserBorrowerForm
    success_url = reverse_lazy('borrowing:create_business')

    def dispatch(self, request, *args, **kwargs):
        """ if the user is already a borrower, redirect to borrowing:home"""
        if BorrowerProfile.objects.filter(user_id=self.request.user.id).exists():
            return HttpResponseRedirect(reverse('borrowing:home'))
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        data = self.request.POST if self.request.method == "POST" else None
        return self.form_class(data=data, user=self.request.user)

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("You are now able to register your business for a loan"))
        return super().form_valid(form)


class BorrowerProfileRequiredMixin(LoginRequiredMixin):
    """
    CBV mixin which verifies that the current user is authenticated and
    has a borrower profile.
    """
    def dispatch(self, request, *args, **kwargs):
        try:
            self.borrower = BorrowerProfile.objects.get(user_id=self.request.user.id)
        except BorrowerProfile.DoesNotExist:
            messages.error(request, _("You must have a valid borrower profile to access this page"))
            return HttpResponseRedirect(reverse('borrowing:home'))
        return super().dispatch(request, *args, **kwargs)


#  ---------------------------------
#         Business Views
#  --------------------------------


class BusinessCreateView(SuccessMessageMixin, BorrowerProfileRequiredMixin, CreateView):
    """ CBV creating a new business for the current user """
    model = Business
    fields = ['name', 'address', 'company_number', 'sector']
    success_message = _("Your business has been successfully added.")
    success_url = reverse_lazy('borrowing:home')
    template_name = "borrowing/create_business_form.html"

    def form_valid(self, form):
        form.instance.owner = self.borrower
        form.save()
        return super().form_valid(form)


class BusinessUpdateView(SuccessMessageMixin, BorrowerProfileRequiredMixin, UpdateView):
    """ CBV to update an existing business -- only possible if the business has
    no related loan and belongs to the user """
    model = Business
    fields = ['name', 'address', 'company_number', 'sector']
    success_message = _("Your business has been successfully edited.")
    success_url = reverse_lazy('borrowing:home')
    template_name = "borrowing/update_business_form.html"

    def get_object(self):
        """
        Only get the Business record for the user making the request
        and only if there is no related loans
        """
        business = get_object_or_404(Business, owner=self.borrower, pk=self.kwargs['pk'])
        if business.loan_set.exists():
            raise SuspiciousOperation(_('You cannot delete a business with existing loans'))
        return business


@login_required
def delete_business(request, pk):
    """ POST only - deletes the business specified if there is no related loans """
    if not request.method == "POST":
        return HttpResponseNotAllowed(['POST', ])
    business = get_object_or_404(Business, owner__user=request.user, pk=pk)
    if business.loan_set.exists():
        raise SuspiciousOperation(_('You cannot delete a business with existing loans'))
    business.delete()
    messages.success(request, _("The business {0} has been deleted").format(business.name))
    return HttpResponseRedirect(reverse('borrowing:home'))


#  ----------------------
#         Loan
#  -----------------------


class LoanCreateView(SuccessMessageMixin, BorrowerProfileRequiredMixin, CreateView):
    """ CBV creating a new loan for the current BorrowerProfile """
    model = Loan
    form_class = LoanForm
    success_message = _(
        "Your loan request was successful and will be reviewed by "
        "our financial services shortly"
    )
    success_url = reverse_lazy('borrowing:home')
    template_name = "borrowing/loan_form.html"

    def get_form(self):
        """
        makes sure the business field can only contain businesses belonging to the current profile
        sets the interest rate to read_only (that should be something taken in charge by javascript)
        it is displayed nonetheless as the user needs to know what she's signing for.
        """
        form = super().get_form()
        form.fields['business'].queryset = Business.objects.filter(owner=self.borrower)
        form.fields['interest_rate'].widget.attrs = {'readonly': True, }
        form.fields['interest_rate'].initial = 0.05
        return form

    def form_valid(self, form):
        form.instance.borrower = self.borrower
        form.save()
        return super().form_valid(form)


class LoanDetailView(BorrowerProfileRequiredMixin, DetailView):
    """
    Simplistic CBV showing a loan and offering an option to cancel it
    if it is still pending
    """
    model = Loan

    def get_object(self):
        # Only get the Business record for the user making the request
        loan = get_object_or_404(Loan, pk=self.kwargs['pk'], borrower=self.borrower)
        return loan


@login_required
def cancel_loan_request(request, pk):
    """
    cancels an existing loan by setting its status to 4
    only if its status was already 0
    """
    if not request.method == "POST":
        return HttpResponseNotAllowed(['POST', ])
    loan = get_object_or_404(Loan, pk=pk, borrower__user=request.user)
    if loan.status != 0:
        raise SuspiciousOperation(_("Processed loans cannot be deleted"))
    loan.status = 4  # status 4 means "cancelled"
    loan.modified_at = timezone.now()
    loan.save()
    messages.success(request, _("The loan request has been cancelled"))
    return HttpResponseRedirect(reverse('borrowing:home'))
