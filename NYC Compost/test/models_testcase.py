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
