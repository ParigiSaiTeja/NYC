from django.urls import reverse
from django.test import TestCase
from django.core import mail

from users.views import ResetPasswordView


class ResetPasswordViewTestCase(TestCase):
    def test_reset_password(self):
        url = reverse('password_reset')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/password_reset.html')

        # Submit the form with a valid email address
        form_data = {'email': 'testuser@example.com'}
        response = self.client.post(url, form_data)

        # Check that the email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [form_data['email']])
        self.assertIn('Password reset on Example.com', mail.outbox[0].subject)

        # Check that the success message is displayed
        self.assertContains(response, "Please check your email for instructions to reset your password.")

        # Check that the user is redirected to the success URL
        self.assertRedirects(response, reverse('users-home'))
