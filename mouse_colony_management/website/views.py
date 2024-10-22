from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .models import *
from .forms import *

# Legal Boiler-plate Views
def terms_of_service(request):
    return render(request, 'legal/terms-of-service.html')
def privacy_policy(request):
    return render(request, 'legal/privacy-policy.html')


@login_required
def home(request):
    return render(request, "home.html", {})

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out...")
    return redirect('index')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('index')  # Redirect to homepage
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

# Generate genetic tree
def genetic_tree(request, mouse_id):
    mouse = get_object_or_404(Mouse, mouse_id=mouse_id)
    ancestors = mouse.get_ancestors()
    descendants = mouse.get_descendants()

    context = {
        'mouse': mouse,
        'ancestors': ancestors,
        'descendants': descendants,
    }
    return render(request, 'genetictree.html', context)

# @login_required
# def dashboard(request):
#     # Get the team of the logged-in user
#     membership = TeamMembership.objects.get(user=request.user)
#     team = membership.team

#     # Filter mice based on team (assuming mice are linked to team via their father/mother)
#     mice = Mouse.objects.filter(father__team=team) | Mouse.objects.filter(mother__team=team)

#     return render(request, 'dashboard.html', {'mice': mice, 'team': team})

# @permission_required('users.is_leader', raise_exception=True)
# @login_required
# def create_mouse(request):
#     if request.method == 'POST':
#         form = MouseForm(request.POST)
#         if form.is_valid():
#             mouse = form.save(commit=False)
#             # Pass the current user to the save method
#             mouse.save(request_user=request.user)
#             return redirect('mouse_list')
#     else:
#         form = MouseForm()
#     return render(request, 'mice/create_mouse.html', {'form': form})