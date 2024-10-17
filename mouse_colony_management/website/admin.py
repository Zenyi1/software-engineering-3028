from django.contrib import admin
from django.contrib.auth.models import User as DefaultUser
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User, Team, TeamMembership, Mouse, Strain, Cage, Breed, BreedingHistory, Genotype, Phenotype

# Register your custom User model with the default UserAdmin options
@admin.register(User)
class CustomUserAdmin(DefaultUserAdmin):
    # Specify the additional fields from your User model to be displayed in admin
    fieldsets = DefaultUserAdmin.fieldsets + (
        (None, {'fields': ('role', 'team')}),
    )

admin.site.register(Team)
admin.site.register(TeamMembership)
admin.site.register(Mouse)
admin.site.register(Strain)
admin.site.register(Cage)
admin.site.register(Breed)
admin.site.register(BreedingHistory)
admin.site.register(Genotype)
admin.site.register(Phenotype)
