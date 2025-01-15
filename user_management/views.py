# user_management/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import UserRegistrationForm, TherapistRegistrationForm, TherapistDetailsForm, LoginForm, UserEditForm
from django.contrib.auth.decorators import login_required
from .forms import TherapistRegistrationForm, TherapistDetailsForm
from .models import Therapist

@login_required
def profile_page_therapist(request):
    therapist = Therapist.objects.get(user=request.user)
    return render(request, 'user_management/profile_page_therapist.html', {'therapist': therapist})

@login_required
def edit_profile_therapist(request):
    therapist = Therapist.objects.get(user=request.user)
    if request.method == 'POST':
        user_form = TherapistRegistrationForm(request.POST, request.FILES, instance=request.user)
        details_form = TherapistDetailsForm(request.POST, request.FILES, instance=therapist)
        if user_form.is_valid() and details_form.is_valid():
            user_form.save()
            details_form.save()
            return redirect('profile_page_therapist')
    else:
        user_form = TherapistRegistrationForm(instance=request.user)
        details_form = TherapistDetailsForm(instance=therapist)
    return render(request, 'user_management/profile_page_therapist_edit.html', {'form': user_form, 'details_form': details_form})

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('profile_page_user')  # Redirect to the profile page
    else:
        form = UserRegistrationForm()
    return render(request, 'user_management/register_user.html', {'form': form})

def register_therapist(request):
    if request.method == 'POST':
        user_form = TherapistRegistrationForm(request.POST, request.FILES)
        details_form = TherapistDetailsForm(request.POST, request.FILES)
        if user_form.is_valid() and details_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            therapist = details_form.save(commit=False)
            therapist.user = user
            therapist.save()
            login(request, user)
            return redirect('profile_page_therapist')
    else:
        user_form = TherapistRegistrationForm()
        details_form = TherapistDetailsForm()
    return render(request, 'user_management/register_therapist.html', {'user_form': user_form, 'details_form': details_form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile_page_user')  # Redirect to the profile page after login
    else:
        form = LoginForm()
    return render(request, 'user_management/login.html', {'form': form})



def base(request):
    return render(request, 'user_management/base.html')


@login_required
def profile_page_user(request):
    return render(request, 'user_management/profile_page_user.html', {'user': request.user})

@login_required
def edit_profile_user(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_page_user')
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'user_management/edit_profile_page_user.html', {'form': form})

