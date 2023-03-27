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

from django.test import TestCase
from django.contrib.auth.models import User
from PIL import Image
from users.models import Profile


class ProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            bio='Test bio',
            avatar='test_avatar.jpg'
        )

    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.bio, 'Test bio')
        self.assertEqual(self.profile.avatar, 'test_avatar.jpg')

    def test_str_representation(self):
        self.assertEqual(str(self.profile), 'testuser')

    def test_avatar_upload_to(self):
        self.assertEqual(
            self.profile.avatar.field.upload_to,
            'profile_images'
        )

    def test_avatar_resizing(self):
        img_path = 'path/to/test_image.jpg'
        img = Image.new('RGB', (200, 200), 'red')
        img.save(img_path)

        self.profile.avatar = img_path
        self.profile.save()

        resized_img = Image.open(self.profile.avatar.path)
        self.assertTrue(resized_img.height <= 100)
        self.assertTrue(resized_img.width <= 100)

        resized_img.close()
        img.close()

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

from django.contrib.auth.models import User
from django.test import TestCase
from users.models import Profile
from users.signals import create_profile, save_profile


class SignalsTestCase(TestCase):
    def test_create_profile_signal(self):
        # Create a new User instance
        user = User.objects.create(username='testuser', password='password')

        # Ensure that no Profile instance exists yet
        self.assertFalse(Profile.objects.filter(user=user).exists())

        # Send the post_save signal for the User instance
        create_profile(sender=User, instance=user, created=True)

        # Ensure that a new Profile instance was created
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_save_profile_signal(self):
        # Create a new User instance with a Profile
        user = User.objects.create(username='testuser', password='password')
        profile = Profile.objects.create(user=user)

        # Change the user's username
        user.username = 'new_username'
        user.save()

        # Send the post_save signal for the User instance
        save_profile(sender=User, instance=user)

        # Ensure that the Profile instance was saved with the new username
        profile.refresh_from_db()
        self.assertEqual(profile.user.username, 'new_username')
