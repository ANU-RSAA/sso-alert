from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views

from .forms.password_change import PasswordChangeCustomForm
from .views import profile, registration


urlpatterns = [
    path('register/', registration, name='register'),
    path('profile/', profile, name='profile'),
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             form_class=PasswordChangeCustomForm,
             template_name='accounts/registration/password_change.html',
         ), name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='accounts/registration/password_change_done.html',
         ), name='password_change_done'),
]
