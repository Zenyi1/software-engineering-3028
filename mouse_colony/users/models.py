from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('leader', 'Leader'),
        ('staff', 'Staff'),
        ('new_staff', 'New Staff'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='new_staff')
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True)

    def clean(self):
        super().clean()  # Call the parent class clean method
        
        # Enforce email domain constraint
        if self.email and not self.email.endswith('@abdn.ac.uk'):
            raise ValidationError(_('Email must be an @abdn.ac.uk address.'))

    def save(self, *args, **kwargs):
        # Ensure the clean method is called before saving
        self.full_clean()  # This calls the clean() method and validates fields
        super().save(*args, **kwargs)
