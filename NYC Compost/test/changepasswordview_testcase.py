from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import Profile
from users.views import ChangePasswordView, profile


class ChangePasswordViewTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123',
        )
        self.client.login(username='testuser', password='password123')
        self.url = reverse('password_change')

    def test_change_password(self):
        # Access the password change page
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/change_password.html')

        # Submit the form with valid data
        form_data = {
            'old_password': 'password123',
            'new_password1': 'newpassword456',
            'new_password2': 'newpassword456',
        }
        response = self.client.post(self.url, form_data)

        # Check that the password was changed successfully
        self.assertRedirects(response, reverse('users-home'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456'))

        # Check that the success message is displayed
        self.assertContains(response, "Password change successful")


class ProfileViewTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123',
        )
        self.client.login(username='testuser', password='password123')
        self.url = reverse('users-profile')
        self.upload_file = SimpleUploadedFile(
            "test_avatar.png",
            b"this is a test image file",
            content_type="image/png"
        )

    def tearDown(self):
        self.upload_file.close()

    def test_profile_get(self):
        # Access the profile page with a GET request
        response = self.client.get(self.url)

        # Check that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check that the correct templates are used
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertTemplateUsed(response, 'users/includes/profile_form.html')

        # # Check that the user and profile forms are in the context
        # self.assertIsInstance(response.context['user_form'], UpdateUserForm)
        # self.assertIsInstance(response.context['profile_form'], UpdateProfileForm)

    def test_profile_post(self):
        # Access the profile page with a POST request and valid form data
        form_data = {
            'username': 'newusername',
            'email': 'newemail@example.com',
            'bio': 'This is a test bio',
            'avatar': self.upload_file,
        }
        response = self.client.post(self.url, form_data)

        # Check that the user and profile data were updated successfully
        self.assertRedirects(response, self.url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newusername')
        self.assertEqual(self.user.email, 'newemail@example.com')
        self.assertEqual(self.user.profile.bio, 'This is a test bio')
        self.assertEqual(self.user.profile.avatar.name, 'profile_images/test_avatar.png')

        # Check that the success message is displayed
        self.assertContains(response, "Profile update successful")
