
from django.urls import path
from .views import register_user, register_therapist, login_view, base, edit_profile_user, profile_page_user, \
    profile_page_therapist, edit_profile_therapist, therapist_list, therapist_detail, user_home, pings_view, \
    user_questionnaire, questionnaire_view

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

]
