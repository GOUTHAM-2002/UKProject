# user_management/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import UserRegistrationForm, TherapistRegistrationForm, TherapistDetailsForm, LoginForm, UserEditForm
from django.contrib.auth.decorators import login_required
from .forms import TherapistRegistrationForm, TherapistDetailsForm
from .models import Therapist, CustomUser, Questionnaire, Question, Answer
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Therapist, Ping

@login_required
def profile_page_therapist(request):
    therapist = Therapist.objects.get(user=request.user)
    # Retrieve all pings for the therapist
    pings = therapist.pings.all()
    return render(request, 'user_management/profile_page_therapist.html', {
        'therapist': therapist,
        'pings': pings,
    })

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
            return redirect('questionnaire')  # Redirect to the profile page
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

            # Check if the logged-in user is a therapist
            if Therapist.objects.filter(user=user).exists():
                return redirect('profile_page_therapist')  # Redirect therapists
            else:
                return redirect('user_home')  # Redirect regular users

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


@login_required
def therapist_list(request):
    therapists = Therapist.objects.all()
    return render(request, 'user_management/therapist_list.html', {'therapists': therapists})




@login_required
def therapist_detail(request, therapist_id):
    therapist = get_object_or_404(Therapist, pk=therapist_id)

    if request.method == "POST" and 'ping' in request.POST:
        # Get the message from the form
        message = request.POST.get('message', '').strip()  # Default to empty string if no message is provided

        # Check if the user has already pinged the therapist
        ping, created = Ping.objects.get_or_create(therapist=therapist, user=request.user)

        if created:
            # If this is a new ping, store the message
            ping.message = message
            ping.save()
            messages.success(request, "You have successfully pinged the therapist!")
        else:
            # If the ping already exists, update the message
            ping.message = message
            ping.save()
            messages.info(request, "You have already pinged this therapist, message updated.")

        return redirect('therapist_detail', therapist_id=therapist_id)

    return render(request, 'user_management/therapist_detail.html', {'therapist': therapist})



@login_required
def user_home(request):
    # You can add any context data you need here
    return render(request, 'user_management/user_home.html')


@login_required
def pings_view(request):
    therapist = get_object_or_404(Therapist, user=request.user)
    pings = therapist.pings.all()
    return render(request, 'user_management/pings.html', {'pings': pings})


@login_required
def questionnaire_view(request):
    questions = Question.objects.all()

    if request.method == "POST":
        for question in questions:
            selected_answer = request.POST.get(str(question.id))
            if selected_answer:
                answer = Answer.objects.get(id=selected_answer)
                Questionnaire.objects.create(user=request.user, question=question, answer=answer)

        return redirect('user_home')

    return render(request, 'user_management/questions.html', {'questions': questions})

def user_questionnaire(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    questionnaires = Questionnaire.objects.filter(user=user)
    return render(request, 'user_management/user_questionarre.html', {
        'user': user,
        'questionnaires': questionnaires
    })