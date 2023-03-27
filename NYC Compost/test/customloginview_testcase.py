from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.forms import LoginForm


class CustomLoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_login_view_get(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertIsInstance(response.context['form'], LoginForm)

    def test_login_view_post_valid_form_without_remember_me(self):
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
            'remember_me': False
        }

        response = self.client.post(self.login_url, data=login_data, follow=True)

        self.assertRedirects(response, reverse('index'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.session.get_expiry_age(), 0)

    def test_login_view_post_valid_form_with_remember_me(self):
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
            'remember_me': True
        }

        response = self.client.post(self.login_url, data=login_data, follow=True)

        self.assertRedirects(response, reverse('index'))
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.session.get_expiry_age(), 1209600)  # 2 weeks in seconds

    def test_login_view_post_invalid_form(self):
        invalid_data = {
            'username': self.user_data['username'],
            'password': 'wrongpassword',
            'remember_me': False
        }

        response = self.client.post(self.login_url, data=invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertContains(response, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')
