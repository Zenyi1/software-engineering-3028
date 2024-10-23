from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from website.models import *

class LegalPagesViewTest(TestCase):

    def test_terms_of_service_view(self):
        response = self.client.get(reverse('terms_of_service'))  # Assuming the name of the URL pattern
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'legal/terms-of-service.html')

    def test_privacy_policy_view(self):
        response = self.client.get(reverse('privacy_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'legal/privacy-policy.html')

class HomeViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_home_view_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/')

    def test_home_view_accessible_if_logged_in(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

class LogoutUserViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_logout_user_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('logout_user'))
        self.assertRedirects(response, reverse('login'))

        # Check if the logout message is present
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have been logged out...")

class RegisterViewTest(TestCase):

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_register_view_post_valid(self):
        form_data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'newuser@abdn.ac.uk',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'role': 'leader'
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertRedirects(response, reverse('index'))
        
        # Check if the user was created
        user_exists = User.objects.filter(username='newuser').exists()
        self.assertTrue(user_exists)

    def test_register_view_post_invalid(self):
        form_data = {
            'username': '',
            'first_name': '',
            'last_name': '',
            'email': 'invalid_email',
            'password1': 'pass',
            'password2': 'different_pass',
            'role': 'leader'
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertFalse(User.objects.filter(username='').exists())  # User shouldn't be created

# class GeneticTreeViewTest(TestCase):

#     def setUp(self):
#         self.mouse = Mouse.objects.create(
#             
#         )

#     def test_genetic_tree_view_valid_mouse(self):
#         response = self.client.get(reverse('genetic_tree', args=[self.mouse.mouse_id]))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'genetictree.html')
#         self.assertContains(response, 'Mouse123')

#     def test_genetic_tree_view_invalid_mouse(self):
#         response = self.client.get(reverse('genetic_tree', args=[999]))  # Non-existent mouse_id
#         self.assertEqual(response.status_code, 404)

