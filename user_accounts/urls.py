from django.urls import path
from . import views

app_name = 'user_accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('password/reset/', views.password_reset_request, name='password_reset_request'),
    path('password/reset/<uuid:token>/', views.password_reset, name='password_reset'),
]
