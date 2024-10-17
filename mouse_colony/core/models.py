# mice/models.py
from django.db import models
import datetime as dt

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from teams.models import TeamMembership  # Import TeamMembership to link users and teams

User = get_user_model()

class Mouse(models.Model):
    SEX_CHOICES = [('M', 'Male'), ('F', 'Female')]
    CLIPPED_CHOICES = [
        ('TL', 'Top Left'),
        ('TR', 'Top Right'),
        ('BL', 'Bottom Left'),
        ('BR', 'Bottom Right'),
    ]
    STATE_CHOICES = [('alive', 'Alive'), ('breeding', 'Breeding'), ('to_be_culled', 'To Be Culled'), ('deceased', 'Deceased')]
    COLOUR_CHOICES = []

    mouse_id = models.AutoField(primary_key=True)  # Unique ID for all mice
    strain = models.ForeignKey('Strain', on_delete=models.CASCADE)
    tube_id = models.IntegerField()  # Managed within each strain
    dob = models.DateField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    father = models.ForeignKey('self', on_delete=models.SET_NULL, limit_choices_to={'sex': 'M'}, null=True, blank=True, related_name='father_of')
    mother = models.ForeignKey('self', on_delete=models.SET_NULL, limit_choices_to={'sex': 'F'}, null=True, blank=True, related_name='mother_of')
    earmark = models.CharField(max_length=20, choices=CLIPPED_CHOICES, blank=True)
    clipped_date = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES)
    cull_date = models.DateTimeField(null=True, blank=True)
    coat = models.CharField(max_length=10, choices=COLOUR_CHOICES)

    cage = models.ForeignKey('Cage', on_delete=models.SET_NULL, null= True, blank=True)

    mouse_keeper = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='kept_mice')

    def save(self, *args, **kwargs):
        # Automatically set the mouse_keeper to the team leader of the user who creates this mouse
        if not self.mouse_keeper:
            # Get the team leader of the current user (who's requesting to create the mouse)
            request_user = kwargs.pop('request_user', None)
            if request_user:
                try:
                    # Find the user's team and get the leader
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

class Strain(models.Model):
    name = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.name

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
        self.male.state = 'active'
        self.male.save()
        self.female.state = 'active'
        self.female.save()
        self.save()

class BreedingHistory(models.Model):
    breed = models.ForeignKey(Breed, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def finish_breeding(self):
        """Set the finished time and update the breed end date."""
        self.finished_at = dt.datetime.now()
        self.breed.end_breeding()  # Call the breed's method to finalize it
        self.save()

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