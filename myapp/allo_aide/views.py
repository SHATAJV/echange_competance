"""
Views for user authentication, homepage display, skill/time slot creation,
and reservation management.

This module defines views to manage user login and logout, render both the
general homepage and user-specific dashboard, and enable functionality
such as creating new skills, time slots, and handling reservations.

Functions:
----------
- `home(request)`: Displays the public homepage with all available skills and time slots.
- `home_user(request)`: Renders the user's dashboard, showing their skills, help requests, and time slots.
- `login_view(request)`: Handles user login, displaying a login form and authenticating credentials.
- `logout_view(request)`: Logs the user out and redirects to the public homepage.
- `create_new_skill(request)`: Allows users to create and save a new skill using `SkillForm`.
- `create_new_request(request)`: Enables users to submit requests for help using `HelpRequestForm`.
- `create_new_proposition(request)`: Lets users propose a new time slot using `TimeSlotForm`.
- `find_slots(request, skill_id, date)`: Retrieves available time slots for a given skill on a specified date.
- `reserve_slot(request, slot_id)`: Reserves a time slot for the logged-in user if it is available.
- `history(request)`: Displays a user's reservation history with associated time slots and skills.
"""

import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404

from .forms import SkillForm, TimeSlotForm, HelpRequestForm
from .models import Skill, TimeSlot, HelpRequest, Reservation


def home(request):
    """
    View to render the homepage, displaying available skills and time slots.

    Context:
        - skills: All available skills.
        - timeslots: Available time slots marked as is_available=True.
    """
    skills = Skill.objects.all()
    timeslots = TimeSlot.objects.filter(is_available=True) 
    return render(request, 'allo_aide/home.html', {'skills': skills, 'timeslots': timeslots})


from django.utils import timezone

def home_user(request):
    user = request.user
    skills = Skill.objects.filter(user=user)
    help_requests = HelpRequest.objects.filter(user=user)
    time_slots = TimeSlot.objects.filter(user=user)

    context = {
        'skills': skills,
        'help_requests': help_requests,
        'time_slots': time_slots,
    }
    return render(request, 'allo_aide/home_user.html', context)
def login_view(request):
    """
    View to handle user login.

    If the request is POST, processes the AuthenticationForm with POST data.
    If valid, logs the user in and redirects them to the home_user page.
    If the request is GET, displays an empty AuthenticationForm.

    Context:
        - form: Instance of AuthenticationForm for login.
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('allo_aide:home_user')
    else:
        form = AuthenticationForm()
    return render(request, 'allo_aide/login.html', {'form': form})


def logout_view(request):
    """
    View to handle user logout, then redirects to the homepage.
    """
    logout(request)
    return redirect('allo_aide:home')


def create_new_skill(request):
    """
    View to create a new skill using SkillForm.

    If the request is POST and form is valid, saves the new skill and redirects
    to the home_user page. Otherwise, displays an empty SkillForm.

    Context:
        - form: Instance of SkillForm for creating a new skill.
    """
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            new_skill = form.save(commit=False)
            new_skill.user = request.user
            new_skill.save()
            return redirect('allo_aide:home_user')
    else:
        form = SkillForm()
    return render(request, 'allo_aide/create_new_skill.html', {'form': form})


def create_new_request(request):
    """
    View to create a new time slot demand using TimeSlotForm.

    If the request is POST and the form is valid, saves the new time slot and redirects
    to the home_user page. Otherwise, displays an empty TimeSlotForm.

    Context:
        - form: Instance of TimeSlotForm for creating a new time slot demand.
    """
    if request.method == "POST":
        form = HelpRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('allo_aide:home_user')
    else:
        form = HelpRequestForm()
    return render(request, 'allo_aide/create_new_demande.html', {'form': form})


def create_new_proposition(request):
    """
    View to create a new time slot demand using TimeSlotForm.

    If the request is POST and the form is valid, saves the new time slot and redirects
    to the home_user page. Otherwise, displays an empty TimeSlotForm.

    Context:
        - form: Instance of TimeSlotForm for creating a new time slot demand.
    """
    if request.method == "POST":
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('allo_aide:home_user')
    else:
        form = TimeSlotForm()
    return render(request, 'allo_aide/create_new_proposition.html', {'form': form})


def find_slots(request, skill_id, date):
    """
    View to find available time slots for a specific skill on a specific date.
    """
    skill = get_object_or_404(Skill, id=skill_id)
    error_message = None

    try:

        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        error_message = 'Invalid date format. Please enter a date in YYYY-MM-DD format.'
        date_obj = None


    if date_obj:
        available_slots = TimeSlot.objects.filter(skill=skill, date=date_obj, is_available=True)
    else:
        available_slots = []

    return render(request, 'allo_aide/find_slots.html', {
        'available_slots': available_slots,
        'skill': skill,
        'date': date_obj,
        'error_message': error_message,
    })


@login_required
def reserve_slot(request, slot_id):

    slot = get_object_or_404(TimeSlot, id=slot_id)


    if slot.is_available:

        reservation = Reservation(time_slot=slot, user=request.user)
        reservation.save()

        slot.is_available = False
        slot.save()

        return redirect('allo_aide:history')
    else:

        return render(request, 'allo_aide/error.html', {'message': 'Ce créneau est déjà réservé.'})

# views.py


@login_required
def history(request):

    reservations = Reservation.objects.filter(user=request.user).select_related('time_slot', 'time_slot__skill')


    context = {
        'reservations': reservations,
    }

    return render(request, 'allo_aide/history.html', context)