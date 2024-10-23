from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime as dt

# # ---------- Role Model ----------
# class Role(models.Model):
#     name = models.CharField(max_length=50)

#     def __str__(self):
#         return self.name
    
# ---------- Cage Model ----------
class Cage(models.Model):
    cage_id = models.AutoField(primary_key=True)
    cage_number = models.CharField(max_length=10, unique=True)
    cage_type = models.CharField(max_length=25)
    location = models.CharField(max_length=25)

    def __str__(self):
        return self.cage_number


# ---------- User Model ----------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('leader', 'Leader'),
        ('staff', 'Staff'),
        ('new_staff', 'New Staff'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='new_staff')

    # Enforce email validation
    def clean(self):
        super().clean()
        if self.email and not self.email.endswith('@abdn.ac.uk'):
            raise ValidationError(_('Email must be an @abdn.ac.uk address.'))

    def save(self, *args, **kwargs):
        self.full_clean()  # Calls the clean method before saving
        super().save(*args, **kwargs)


# ---------- Team Model ----------
class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
# ---------- Team Membership ----------
class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ("user", "team")

    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.user.role})"


# # ---------- Researcher Profile ----------
# class ResearcherProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     role = models.ForeignKey(Role, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.user.username} - {self.role.name}"


# # Signal to create a ResearcherProfile when a User is created
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         default_role = Role.objects.get(name='New Staff')  # Ensure 'New Staff' role exists
#         ResearcherProfile.objects.create(user=instance, role=default_role)


# ---------- Mouse Model ----------
class Mouse(models.Model):
    SEX_CHOICES = [('M', 'Male'), ('F', 'Female')]
    CLIPPED_CHOICES = [
        ('TL', 'Top Left'),
        ('TR', 'Top Right'),
        ('BL', 'Bottom Left'),
        ('BR', 'Bottom Right'),
    ]
    STATE_CHOICES = [('alive', 'Alive'), ('breeding', 'Breeding'), ('to_be_culled', 'To Be Culled'), ('deceased', 'Deceased')]

    mouse_id = models.AutoField(primary_key=True)
    strain = models.ForeignKey('Strain', on_delete=models.CASCADE)
    tube_id = models.IntegerField()
    dob = models.DateField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    father = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='father_of', limit_choices_to={'sex': 'M'})
    mother = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='mother_of', limit_choices_to={'sex': 'F'})
    earmark = models.CharField(max_length=20, choices=CLIPPED_CHOICES, blank=True)
    clipped_date = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=12, choices=STATE_CHOICES)
    cull_date = models.DateTimeField(null=True, blank=True)
    mouse_keeper = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='kept_mice')

    class Meta:
        unique_together = ('strain', 'tube_id')

    def __str__(self):
        return f"Mouse {self.mouse_id} - {self.strain} - Tube {self.tube_id}"
    
    def get_ancestors(self):
        ancestors = []
        if self.mother:
            ancestors.append(self.mother)
            ancestors.extend(self.mother.get_ancestors())
        if self.father:
            ancestors.append(self.father)
            ancestors.extend(self.father.get_ancestors())
        return ancestors

    def get_descendants(self):
        descendants = list(self.mother_of.all()) + list(self.father_of.all())
        for child in descendants:
            descendants.extend(child.get_descendants())
        return descendants


# ---------- Request Model ----------
class Request(models.Model):
    REQUEST_TYPES = [
        ('breed', 'Breeding Request'),
        ('cull', 'Culling Request'),
        # ('end_breed', 'End Breeding Request'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    request_id = models.AutoField(primary_key=True)
    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    mouse = models.ForeignKey(Mouse, on_delete=models.CASCADE, related_name='primary_mouse_requests')
    second_mouse = models.ForeignKey(Mouse, on_delete=models.CASCADE, null=True, blank=True, related_name='secondary_mouse_requests', help_text="For breeding requests, select a second mouse of the opposite sex.")
    cage = models.ForeignKey(Cage, on_delete=models.CASCADE, null=True, blank=True, help_text="Required for breeding requests.")
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comments = models.TextField(blank=True, null=True)

    def clean(self):
        """Custom validation for the request model."""
        # Ensure second_mouse is provided only for breeding requests
        if self.request_type == 'breed':
            if not self.second_mouse:
                raise ValidationError("Breeding requests must specify a second mouse.")
            # Ensure the two mice are of opposite sex
            if self.mouse.sex == self.second_mouse.sex:
                raise ValidationError("For breeding requests, the two mice must be of opposite sexes.")
            # Ensure a cage is provided for breeding requests
            if not self.cage:
                raise ValidationError("A cage must be specified for breeding requests.")
        elif self.request_type == 'cull':
            if self.second_mouse:
                raise ValidationError("Culling requests should not have a second mouse.")
            # Ensure that cage is not set for non-breeding requests
            if self.cage:
                raise ValidationError(f"A cage should not be specified for {self.request_type} requests.")

        super().clean()

    def __str__(self):
        if self.request_type == 'breed':
            return f"Breeding Request: {self.mouse.mouse_id} with {self.second_mouse.mouse_id} by {self.requester.username}"
        return f"{self.request_type} Request by {self.requester.username} for Mouse {self.mouse.mouse_id}"

    def approve(self):
        self.status = 'approved'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

    def complete(self):
        self.status = 'completed'
        self.save()

        # Handle culling request completion
        if self.request_type == 'cull':
            self.mouse.state = 'deceased'
            self.mouse.cull_date = dt.datetime.now()
            self.mouse.save()

        # Handle breeding request completion
        if self.request_type == 'breed':
            self.mouse.state = 'breeding'  # Update first mouse to breeding state
            self.second_mouse.state = 'breeding'  # Update second mouse to breeding state
            self.mouse.save()
            self.second_mouse.save()

            # Create a new Breed instance
            Breed.objects.create(
                male=self.mouse,
                female=self.second_mouse,
                cage=self.cage,
            )

        # # Handle end breeding request completion
        # if self.request_type == 'end_breed':
        #     self.mouse.state = 'alive'  # Update first mouse to alive state
        #     self.second_mouse.state = 'alive'  # Update second mouse to alive state
        #     self.mouse.save()
        #     self.second_mouse.save()
           

# ---------- Breed Model ----------
class Breed(models.Model):
    breed_id = models.AutoField(primary_key=True)
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
        return f"Breeding {self.male.mouse_id} x {self.female.mouse_id}"

# ---------- Strain Model ----------
class Strain(models.Model):
    name = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.name
    
# ---------- Genotype Model ----------
class Genotype(models.Model):
    mouse = models.ForeignKey(Mouse, on_delete=models.CASCADE, related_name='genotypes')
    gene = models.CharField(max_length=50)  # The gene or marker being tested
    allele_1 = models.CharField(max_length=50)  # First allele
    allele_2 = models.CharField(max_length=50)  # Second allele
    test_date = models.DateField(auto_now_add=True)  # Date the test was performed

    def __str__(self):
        return f"{self.mouse.mouse_id} - {self.gene}: {self.allele_1}/{self.allele_2}"


# ---------- Phenotype Model ----------
class Phenotype(models.Model):
    mouse = models.ForeignKey(Mouse, on_delete=models.CASCADE, related_name='phenotypes')
    characteristic = models.CharField(max_length=100)  # The observable trait, e.g., "Coat Color"
    description = models.CharField(max_length=255)  # A description of the phenotype
    observation_date = models.DateField(auto_now_add=True)  # Date the phenotype was observed

    def __str__(self):
        return f"{self.mouse.mouse_id} - {self.characteristic}: {self.description}"

