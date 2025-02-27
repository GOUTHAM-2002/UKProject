# user_management/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import UserRegistrationForm, TherapistRegistrationForm, TherapistDetailsForm, LoginForm, UserEditForm, PostForm
from django.contrib.auth.decorators import login_required
from .forms import TherapistRegistrationForm, TherapistDetailsForm
from .models import Therapist, CustomUser, Questionnaire, Question, Answer, Message, ChatMessage, Post
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Therapist, Ping
from django.db import models
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.http import JsonResponse
import google.generativeai as genai
from datetime import timedelta
from django.utils import timezone
from .models import UserGeminiChat, CustomUser
from django.shortcuts import get_object_or_404
import json

from django.conf import settings  # Add this at the top with other imports


@login_required
def user_analytics_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    chats_count = UserGeminiChat.objects.filter(user=user).count()
    questionnaires = Questionnaire.objects.filter(user=user)
    
    return render(request, 'user_management/user_analytics.html', {
        'user': user,
        'chats_count': chats_count,
        'questionnaires': questionnaires
    })
@login_required
def generate_insights(request, user_id):
    try:
        print(f"\n=== Generating Weekly Insights ===")
        print(f"User ID: {user_id}")
        
        user = get_object_or_404(CustomUser, id=user_id)
        print(f"Found user: {user.email}")
        
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        print("Configured Gemini API")
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("Created Gemini model")
        
        # Get last week's chats
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        print(f"Searching for chats between {start_date} and {end_date}")
        
        chats = UserGeminiChat.objects.filter(
            user_id=user_id,
            timestamp__range=(start_date, end_date)
        ).order_by('timestamp')
        print(f"Found {chats.count()} chats")

        if not chats.exists():
            print("No chats found - returning empty data")
            return JsonResponse({
                'dates': [],
                'sentiment_scores': [],
                'topics': [],
                'insights': [{
                    'title': 'No Data Available',
                    'description': 'No chat history found for the past week.',
                    'icon': 'fa-info-circle'
                }]
            })

        # Prepare chat history for analysis
        chat_history = "\n".join([
            f"User: {chat.user_message}\nGemini: {chat.gemini_response}"
            for chat in chats
        ])
        print(f"Analyzing {len(chats)} chat messages")

        # Generate insights using Gemini
        prompt = """
        Analyze this chat history and provide insights. Return a JSON object with exactly these keys:
        {
            "sentiment_scores": [numbers between 0-1 representing emotional state for each message],
            "topics": [{"name": "topic name", "count": number of occurrences}],
            "insights": [{"title": "insight title", "description": "detailed observation", "icon": "font-awesome-icon-name"}]
        }
        Focus on emotional patterns, recurring themes, and progress indicators.
        Chat History:
        """ + chat_history

        print("Sending request to Gemini")
        response = model.generate_content(prompt)
        print(f"Received Gemini response: {response.text[:200]}...")

        try:
            # Clean the response text by removing markdown code blocks
            cleaned_response = response.text.replace('```json', '').replace('```', '').strip()
            print(f"Cleaned response: {cleaned_response[:200]}...")
            
            analysis = json.loads(cleaned_response)
            print("Successfully parsed Gemini response as JSON")

            result = {
                'dates': [chat.timestamp.strftime('%Y-%m-%d') for chat in chats],
                'sentiment_scores': analysis.get('sentiment_scores', []),
                'topics': analysis.get('topics', []),
                'insights': analysis.get('insights', [])
            }
            print("Prepared final response")
            return JsonResponse(result)

        except json.JSONDecodeError as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Raw response that couldn't be parsed: {response.text}")
            return JsonResponse({
                'error': 'Failed to parse analysis results'
            }, status=500)

    except Exception as e:
        print(f"Error in generate_insights: {str(e)}")
        return JsonResponse({
            'error': str(e)
        }, status=500)
@login_required
def profile_page_therapist(request):
    therapist = request.user.therapist
    chat_partners_count = CustomUser.objects.filter(
        models.Q(chat_sent_messages__receiver=request.user) | 
        models.Q(chat_received_messages__sender=request.user)
    ).distinct().count()
    
    context = {
        'therapist': therapist,
        'pings': Ping.objects.filter(therapist=therapist).order_by('-timestamp'),
        'chat_partners_count': chat_partners_count
    }
    return render(request, 'user_management/profile_page_therapist.html', context)

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
                return redirect('profile_page_user')  # Redirect regular users

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

@login_required
def research_view(request):
    # Dummy articles data
    articles = [
        {
            'title': 'Mental Health in Construction: Breaking the Silence',
            'summary': 'Understanding the unique challenges faced by UK construction workers and strategies for maintaining mental wellbeing.',
            'icon': 'fa-hard-hat',
            'color': 'rgba(147, 51, 234, 0.7)'  # Purple shade
        },
        {
            'title': 'Stress Management on Construction Sites',
            'summary': 'Practical techniques for managing workplace stress and maintaining work-life balance in the construction industry.',
            'icon': 'fa-brain',
            'color': 'rgba(126, 34, 206, 0.7)'  # Darker purple
        },
        {
            'title': 'Building Resilience: A Worker\'s Guide',
            'summary': 'Tips and strategies for building mental resilience while working in challenging construction environments.',
            'icon': 'fa-shield-alt',
            'color': 'rgba(168, 85, 247, 0.7)'  # Lighter purple
        },
        {
            'title': 'Daily Inspirational Quotes',
            'quotes': [
                '"Your mental health is a priority. Your happiness is essential. Your self-care is a necessity."',
                '"Taking care of yourself isn\'t selfish, it\'s essential."',
                '"You are stronger than you think."'
            ],
            'icon': 'fa-quote-right',
            'color': 'rgba(139, 92, 246, 0.7)'  # Another purple shade
        }
    ]
    return render(request, 'user_management/research.html', {'articles': articles})

@login_required
def chat_view(request):
    user = request.user
    
    if hasattr(user, 'therapist'):
        # For therapists, show users who have either pinged them or have ongoing chats
        chat_partners = CustomUser.objects.filter(
            models.Q(chat_sent_messages__receiver=user) | 
            models.Q(chat_received_messages__sender=user) |
            models.Q(pinged_therapists__therapist=user.therapist)
        ).distinct().order_by('-chat_sent_messages__timestamp')
    else:
        # For regular users, show all therapists
        chat_partners = CustomUser.objects.filter(
            therapist__isnull=False
        ).distinct()

    return render(request, 'user_management/chat.html', {
        'chat_partners': chat_partners,
    })

@login_required
def get_messages(request, partner_id):
    try:
        partner = CustomUser.objects.get(id=partner_id)
        messages = ChatMessage.objects.filter(
            (models.Q(sender=request.user, receiver=partner) |
             models.Q(sender=partner, receiver=request.user))
        ).order_by('timestamp')
        
        # Mark messages as read
        messages.filter(receiver=request.user).update(is_read=True)
        
        return JsonResponse([{
            'content': msg.content,
            'sender': msg.sender_id == request.user.id,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'is_read': msg.is_read
        } for msg in messages], safe=False)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

@login_required
def send_message(request, partner_id):
    if request.method == 'POST':
        content = request.POST.get('message', '').strip()
        try:
            partner = CustomUser.objects.get(id=partner_id)
            if content:
                ChatMessage.objects.create(
                    sender=request.user,
                    receiver=partner,
                    content=content
                )
                return JsonResponse({'status': 'success'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def start_chat(request):
    if request.method == 'POST':
        therapist_id = request.POST.get('therapist_id')
        try:
            therapist = Therapist.objects.get(id=therapist_id)
            ping, created = Ping.objects.get_or_create(
                therapist=therapist,
                user=request.user,
                defaults={'message': "Started a conversation"}
            )
            if created:
                ChatMessage.objects.create(
                    ping=ping,
                    sender=request.user,
                    content="Hi, I would like to start a conversation."
                )
            return JsonResponse({
                'status': 'success',
                'ping_id': ping.id,
                'therapist_name': therapist.name
            })
        except Therapist.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def therapist_chat_view(request):
    if not hasattr(request.user, 'therapist'):
        return redirect('chat')
        
    # Get users who have either messaged or pinged this therapist
    chat_partners = CustomUser.objects.filter(
        models.Q(chat_sent_messages__receiver=request.user) | 
        models.Q(chat_received_messages__sender=request.user) |
        models.Q(pinged_therapists__therapist=request.user.therapist)
    ).distinct().annotate(
        last_message_time=models.Max('chat_sent_messages__timestamp'),
        last_message=models.Subquery(
            ChatMessage.objects.filter(
                models.Q(sender=models.OuterRef('id'), receiver=request.user) |
                models.Q(sender=request.user, receiver=models.OuterRef('id'))
            ).order_by('-timestamp').values('content')[:1]
        ),
        unread_count=models.Count(
            'chat_sent_messages',
            filter=models.Q(chat_sent_messages__receiver=request.user, chat_sent_messages__is_read=False)
        )
    ).order_by('-last_message_time')

    return render(request, 'user_management/therapist_chat.html', {
        'chat_partners': chat_partners,
    })

@login_required
def posts_list(request):
    sort_by = request.GET.get('sort', 'recent')
    if sort_by == 'most_upvoted':
        posts = Post.objects.order_by('-upvote_count')
    else:
        posts = Post.objects.order_by('-created_at')
    
    # Check if the user is a therapist
    is_therapist = hasattr(request.user, 'therapist')
    
    # Use different base templates for therapist and regular users
    base_template = 'user_management/base_with_nav_therapist.html' if is_therapist else 'user_management/base_with_nav.html'
    
    return render(request, 'user_management/posts_list.html', {
        'posts': posts,
        'sort_by': sort_by,
        'base_template': base_template,
        'is_therapist': is_therapist  # Pass this to template
    })


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the current user is the author
    if request.user.therapist != post.author:
        return redirect('posts_list')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            
            post_type = form.cleaned_data['post_type']
            if post_type == 'article':
                post.media_file = None
                post.thumbnail = None
            elif post_type == 'image':
                post.thumbnail = None
                if 'media_file' in request.FILES:
                    post.media_file = request.FILES['media_file']
            elif post_type == 'video':
                if 'media_file' in request.FILES:
                    post.media_file = request.FILES['media_file']
                if 'thumbnail' in request.FILES:
                    post.thumbnail = request.FILES['thumbnail']
            
            post.save()
            return redirect('posts_list')
    else:
        form = PostForm(instance=post)
    
    return render(request, 'user_management/create_post.html', {
        'form': form,
        'editing': True,
        'post': post
    })

@login_required
def delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        
        # Check if the current user is the author
        if request.user.therapist == post.author:
            post.delete()
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=403)

@login_required
def create_post(request):
    if not hasattr(request.user, 'therapist'):
        return redirect('posts_list')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.therapist
            
            post_type = form.cleaned_data['post_type']
            if post_type == 'article':
                post.media_file = None
                post.thumbnail = None
            elif post_type == 'image':
                post.thumbnail = None  # No thumbnail needed for images
                if 'media_file' in request.FILES:
                    post.media_file = request.FILES['media_file']
            elif post_type == 'video':
                if 'media_file' in request.FILES:
                    post.media_file = request.FILES['media_file']
                if 'thumbnail' in request.FILES:
                    post.thumbnail = request.FILES['thumbnail']
            
            post.save()
            return redirect('posts_list')
    else:
        form = PostForm()
    
    return render(request, 'user_management/create_post.html', {'form': form})

@login_required
def upvote_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.upvotes.all():
        post.upvotes.remove(request.user)
    else:
        post.upvotes.add(request.user)
    post.update_upvote_count()
    return JsonResponse({'upvotes': post.upvote_count})