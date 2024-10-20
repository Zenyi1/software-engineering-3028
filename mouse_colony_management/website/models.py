# core/models.py
from django.db import models
import datetime as dt
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = [
        ('leader', 'Leader'),
        ('staff', 'Staff'),
        ('new_staff', 'New Staff'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='new_staff')
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True)

    # Use unique related_name to avoid clashes with auth.User
    groups = models.ManyToManyField(
        Group,
        related_name='website_user_set',  # Add a unique related_name for 'groups'
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='website_user_permissions_set',  # Add a unique related_name for 'permissions'
        blank=True,
        help_text='Specific permissions for this user.'
    )

    def clean(self):
        super().clean()  # Call the parent class clean method
        
        # Enforce email domain constraint
        if self.email and not self.email.endswith('@abdn.ac.uk'):
            raise ValidationError(_('Email must be an @abdn.ac.uk address.'))

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure validation is called before saving
        super().save(*args, **kwargs)

    @classmethod
    def create_default_groups(cls):
        # Ensure groups exist
        leader_group, _ = Group.objects.get_or_create(name='Leader')
        staff_group, _ = Group.objects.get_or_create(name='Staff')
        new_staff_group, _ = Group.objects.get_or_create(name='New Staff')

        # Set permissions for each group
        team_permissions = Permission.objects.filter(codename__in=['add_team', 'change_team', 'view_team', 'delete_team'])
        membership_permissions = Permission.objects.filter(codename__in=['add_teammembership', 'change_teammembership', 'view_teammembership', 'delete_teammembership'])

        leader_group.permissions.add(*team_permissions, *membership_permissions)
        staff_group.permissions.add(
            Permission.objects.get(codename='view_team'), 
            Permission.objects.get(codename='view_teammembership')
        )
        new_staff_group.permissions.add(
            Permission.objects.get(codename='view_team'), 
            Permission.objects.get(codename='view_teammembership')
        )

    def __str__(self):
        return self.username  # Display username in the admin


class TeamMembership(models.Model):
    ROLE_CHOICES = [
        ('leader', 'Leader'),
        ('staff', 'Staff'),
        ('new_staff', 'New Staff'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'team')

    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.role})"


class Strain(models.Model):
    name = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.name


class Mouse(models.Model):
    SEX_CHOICES = [('M', 'Male'), ('F', 'Female')]
    CLIPPED_CHOICES = [
        ('TL', 'Top Left'),
        ('TR', 'Top Right'),
        ('BL', 'Bottom Left'),
        ('BR', 'Bottom Right'),
    ]
    STATE_CHOICES = [('alive', 'Alive'), ('breeding', 'Breeding'), ('to_be_culled', 'To Be Culled'), ('deceased', 'Deceased')]
    
    mouse_id = models.AutoField(primary_key=True)  # Unique ID for all mice
    strain = models.ForeignKey(Strain, on_delete=models.CASCADE)
    tube_id = models.IntegerField()  # Managed within each strain
    dob = models.DateField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    father = models.ForeignKey('self', on_delete=models.SET_NULL, limit_choices_to={'sex': 'M'}, null=True, blank=True, related_name='father_of')
    mother = models.ForeignKey('self', on_delete=models.SET_NULL, limit_choices_to={'sex': 'F'}, null=True, blank=True, related_name='mother_of')
    earmark = models.CharField(max_length=20, choices=CLIPPED_CHOICES, blank=True)
    clipped_date = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=12, choices=STATE_CHOICES)
    cull_date = models.DateTimeField(null=True, blank=True)

    mouse_keeper = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='kept_mice')

    def save(self, *args, **kwargs):
        # Automatically assign a mouse keeper if not provided
        if not self.mouse_keeper:
            request_user = kwargs.pop('request_user', None)
            if request_user:
                try:
                    team_membership = TeamMembership.objects.get(user=request_user)
                    leader_membership = TeamMembership.objects.get(team=team_membership.team, role='leader')
                    self.mouse_keeper = leader_membership.user
                except TeamMembership.DoesNotExist:
                    pass  # Handle case where no team or leader is found
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('strain', 'tube_id')

    def __str__(self):
        return f"Mouse {self.mouse_id} - {self.strain} - Tube {self.tube_id}"


class Cage(models.Model):
    cage_id = models.AutoField(primary_key=True)
    cage_number = models.CharField(max_length=10, unique=True)
    cage_type = models.CharField(max_length=25)
    location = models.CharField(max_length=25)

    def __str__(self):
        return self.cage_number


class Breed(models.Model):
    breed_id = models.CharField(max_length=15, primary_key=True)
    male = models.ForeignKey(Mouse, on_delete=models.CASCADE, limit_choices_to={'sex': 'M'}, related_name='male_breeds')
    female = models.ForeignKey(Mouse, on_delete=models.CASCADE, limit_choices_to={'sex': 'F'}, related_name='female_breeds')
    cage = models.ForeignKey(Cage, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def end_breeding(self):
        """Set the breeding as finished and update mouse states."""
        self.end_date = dt.datetime.now()
        self.male.state = 'alive'  # Adjusted from 'active' to a valid state
        self.female.state = 'alive'  # Adjusted from 'active' to a valid state
        self.male.save()
        self.female.save()
        self.save()

    def __str__(self):
        return f"Breed {self.breed_id} - {self.male} x {self.female}"


class BreedingHistory(models.Model):
    breed = models.ForeignKey(Breed, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def finish_breeding(self):
        """Set the finished time and update the breed end date."""
        self.finished_at = dt.datetime.now()
        self.breed.end_breeding()  # Call the breed's method to finalize it
        self.save()

    def __str__(self):
        return f"Breeding History for {self.breed}"


# Signal to create BreedingHistory automatically when Breed is created
@receiver(post_save, sender=Breed)
def create_breeding_history(sender, instance, created, **kwargs):
    if created:
        # Create a BreedingHistory instance linked to this Breed
        BreedingHistory.objects.create(breed=instance)

        # Update both mice to 'breeding' state
        instance.male.state = 'breeding'
        instance.male.save()
        instance.female.state = 'breeding'
        instance.female.save()


class Genotype(models.Model):
    mouse = models.ForeignKey(Mouse, on_delete=models.CASCADE, related_name='genotypes')
    gene = models.CharField(max_length=50)  # The gene or marker being tested
    allele_1 = models.CharField(max_length=50)  # First allele
    allele_2 = models.CharField(max_length=50)  # Second allele
    test_date = models.DateField(auto_now_add=True)  # Date the test was performed

    def __str__(self):
        return f"{self.mouse.mouse_id} - {self.gene}: {self.allele_1}/{self.allele_2}"


class Phenotype(models.Model):
    mouse = models.ForeignKey(Mouse, on_delete=models.CASCADE, related_name='phenotypes')
    characteristic = models.CharField(max_length=100)  # The observable trait, e.g., "Coat Color"
    description = models.CharField(max_length=255)  # A description of the phenotype
    observation_date = models.DateField(auto_now_add=True)  # Date the phenotype was observed

    def __str__(self):
        return f"{self.mouse.mouse_id} - {self.characteristic}: {self.description}"

