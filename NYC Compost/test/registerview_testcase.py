from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.forms import RegisterForm


class RegisterViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

    def test_register_view_get(self):
        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIsInstance(response.context['form'], RegisterForm)

    def test_register_view_post_valid_form(self):
        response = self.client.post(self.register_url, data=self.user_data)

        self.assertRedirects(response, reverse('login'))
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, self.user_data['username'])
        self.assertEqual(len(response.client.session['_auth_user_id']), 1)
        self.assertContains(response, 'Account created for')

    def test_register_view_post_invalid_form(self):
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'wrongpassword'

        response = self.client.post(self.register_url, data=invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertContains(response, 'Please correct the errors below.')

    def test_register_view_redirect_if_logged_in(self):
        self.client.force_login(User.objects.create_user(**self.user_data))

        response = self.client.get(self.register_url)

        self.assertRedirects(response, '/')
