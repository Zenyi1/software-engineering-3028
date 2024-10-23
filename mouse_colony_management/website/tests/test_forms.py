from django.test import TestCase
from website.forms import RegistrationForm  # Assuming you have a form like this

class TestRegistrationForm(TestCase):

    def test_registration_form_valid_data(self):
        """Test that valid form data passes validation."""
        form_data = {
            'username': 'testuser',
            'first_name': 'test',
            'last_name': 'user',
            'email': 'testuser@abdn.ac.uk',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'role': 'new_staff',
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_invalid_data(self):
        """Test that invalid form data raises a validation error."""
        form_data = {
            'username': '',
            'first_name': '',
            'last_name': '',
            'email': 'not-an-email',
            'password1': '123',
            'password2': '456',  # Passwords don't match
            'role': '',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password2', form.errors)
        self.assertIn('role', form.errors)

    def test_clean_email_valid(self):
        """Test that a valid @abdn.ac.uk email passes validation."""
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'testuser@abdn.ac.uk',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'role': 'leader',
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())  # The form should be valid with a correct email

    def test_clean_email_invalid(self):
        """Test that an invalid email not ending with @abdn.ac.uk raises a validation error."""
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'testuser@gmail.com',  # Invalid domain
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'role': 'leader',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())  # The form should be invalid due to the wrong email
        self.assertIn('email', form.errors)  # There should be an error for the email field
        self.assertEqual(form.errors['email'], ['Email must be an @abdn.ac.uk address.'])


    
