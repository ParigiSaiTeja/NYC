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
