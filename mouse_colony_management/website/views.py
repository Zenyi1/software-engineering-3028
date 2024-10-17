from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .models import *


@login_required
def home(request):
    return render(request, "home.html", {})

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out...")
    return redirect('index')

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