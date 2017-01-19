from django.core.urlresolvers import reverse, resolve

from test_plus.test import TestCase


class TestUserURLs(TestCase):
    """Test URL patterns for users app."""
        

    def test_activate_account_resolve(self):
        """ /borrowing/activate/ should resolve to borrowing:activate_account """
        self.assertEqual(resolve('/borrowing/activate/').view_name, 'borrowing:activate_account')
    
    def test_activate_account_reverse(self):
        """ borrowing:activate_account should reverse to /borrowing/activate/ """
        self.assertEqual(
            reverse('borrowing:activate_account', kwargs={}),
            '/borrowing/activate/'
        )

    # -------------------
    # Businesses
    #--------------------
    
    # New business
    def test_new_business_resolve(self):
        """ /borrowing/new-business/ should resolve to borrowing:create_business """
        self.assertEqual(resolve('/borrowing/new-business/').view_name, 'borrowing:create_business')
    
    def test_new_business_reverse(self):
        """ borrowing:create_business should reverse to /borrowing/new-business/ """
        self.assertEqual(
            reverse('borrowing:create_business', kwargs={}),
            '/borrowing/new-business/'
        )
        
    # Update business
    def test_update_business_resolve(self):
        """ /borrowing/update-business/42/ should resolve to borrowing:update_business """
        self.assertEqual(resolve('/borrowing/update-business/42/').view_name, 'borrowing:update_business')
    
    def test_update_business_reverse(self):
        """ borrowing:update_business should reverse to /borrowing/update-business/42/ """
        self.assertEqual(
            reverse('borrowing:update_business', kwargs={'pk': 42}),
            '/borrowing/update-business/42/'
        )
        
    # Delete business
    def test_delete_business_resolve(self):
        """ /borrowing/delete-business/ should resolve to borrowing:delete_business """
        self.assertEqual(resolve('/borrowing/delete-business/42/').view_name, 'borrowing:delete_business')
    
    def test_delete_business_reverse(self):
        """ borrowing:delete_business should reverse to /borrowing/delete-business/ """
        self.assertEqual(
            reverse('borrowing:delete_business', kwargs={'pk': 42}),
            '/borrowing/delete-business/42/'
        )

    #---------------------------
    #        Loans
    #---------------------------

    # New Loan
    def test_new_loan_resolve(self):
        """ /borrowing/new-loan/ should resolve to borrowing:create_loan """
        self.assertEqual(resolve('/borrowing/new-loan/').view_name, 'borrowing:create_loan')
    
    def test_new_loan_reverse(self):
        """ borrowing:create_loan should reverse to /borrowing/new-loan/ """
        self.assertEqual(
            reverse('borrowing:create_loan', kwargs={}),
            '/borrowing/new-loan/'
        )
    
    # Loan detail
    def test_loan_detail_resolve(self):
        """ /borrowing/loan-detail/42/ should resolve to borrowing:loan_detail """
        self.assertEqual(resolve('/borrowing/loan-detail/42/').view_name, 'borrowing:loan_detail')
    
    def test_loan_detail_reverse(self):
        """ borrowing:loan_detail should reverse to /borrowing/loan-detail/42/ """
        self.assertEqual(
            reverse('borrowing:loan_detail', kwargs={'pk': 42}),
            '/borrowing/loan-detail/42/'
        )

    # Loan Deletion
    def test_cancel_loan_resolve(self):
        """ /borrowing/cancel-loan/42/ should resolve to borrowing:cancel_loan """
        self.assertEqual(resolve('/borrowing/cancel-loan/42/').view_name, 'borrowing:cancel_loan')
    
    def test_cancel_loan_reverse(self):
        """ borrowing:cancel_loan should reverse to /borrowing/cancel-loan/42/ """
        self.assertEqual(
            reverse('borrowing:cancel_loan', kwargs={'pk': 42}),
            '/borrowing/cancel-loan/42/'
        )

    #-------------------------
    #    Verify Phone
    #-------------------------

    # Loan Deletion
    def test_verify_phone_resolve(self):
        """ /borrowing/verify-phone/ should resolve to borrowing:verify_phone """
        self.assertEqual(resolve('/borrowing/verify-phone/').view_name, 'borrowing:verify_phone')
    
    def test_verify_phone_reverse(self):
        """ borrowing:verify_phone should reverse to /borrowing/verify-phone/ """
        self.assertEqual(
            reverse('borrowing:verify_phone', kwargs={}),
            '/borrowing/verify-phone/'
        )
