from django.urls import path


from .views import delete_post, edit_post, register_user, register_therapist, login_view, base, edit_profile_user, profile_page_user, \
    profile_page_therapist, edit_profile_therapist, therapist_list, therapist_detail, user_home, pings_view, \
    user_questionnaire, questionnaire_view, research_view, chat_view, get_messages, send_message, start_chat, \
    therapist_chat_view, posts_list, create_post, upvote_post
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/user/', register_user, name='register_user'),
    path('register/therapist/', register_therapist, name='register_therapist'),
    path('login/', login_view, name='login'),
    path('auth/', base, name='base'),
    path('profile/user/', profile_page_user, name='profile_page_user'),
    path('profile/edit/user/', edit_profile_user, name='edit_profile_user'),
    path('profile/therapist/', profile_page_therapist, name='profile_page_therapist'),
    path('profile/therapist/edit/', edit_profile_therapist, name='edit_profile_therapist'),
    path('therapists/', therapist_list, name='therapist_list'),
    path('therapist/<int:therapist_id>/', therapist_detail, name='therapist_detail'),
    path('user_home/', user_home, name='user_home'),
    path('pings/', pings_view, name='pings'),
    path('user/<int:user_id>/questionnaire/', user_questionnaire, name='user_questionnaire'),
    path('questionnaire/', questionnaire_view, name='questionnaire'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('research/', research_view, name='research'),
    path('chat/', chat_view, name='chat'),
    path('chat/messages/<int:partner_id>/', get_messages, name='get_messages'),
    path('chat/send/<int:partner_id>/', send_message, name='send_message'),
    path('start-chat/', start_chat, name='start_chat'),
    path('therapist/chat/', therapist_chat_view, name='therapist_chat'),
    path('posts/', posts_list, name='posts_list'),
    path('posts/create/', create_post, name='create_post'),
    path('posts/upvote/<int:post_id>/', upvote_post, name='upvote_post'),
    path('posts/edit/<int:post_id>/', edit_post, name='edit_post'),
path('posts/delete/<int:post_id>/', delete_post, name='delete_post'),
]
