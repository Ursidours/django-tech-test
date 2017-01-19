from django.core.urlresolvers import reverse, resolve

from test_plus.test import TestCase


class TestUserURLs(TestCase):
    """Test URL patterns for users app."""

    def setUp(self):
        self.user = self.make_user()

    def test_redirect_reverse(self):
        """users:redirect should reverse to /users/~redirect/."""
        self.assertEqual(reverse('users:redirect'), '/users/~redirect/')

    def test_redirect_resolve(self):
        """/users/~redirect/ should resolve to users:redirect."""
        self.assertEqual(
            resolve('/users/~redirect/').view_name,
            'users:redirect'
        )
