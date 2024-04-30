from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views

from .views import SingleObservationCreateView, ChainListView, ChainCreateView, ChainView, ChainedTargetDetailView

app_name = 'chains'

urlpatterns = [
    path('add/', ChainCreateView.as_view(), name='add_chain'),
    path('', ChainListView.as_view(), name='chain_list'),
    path('<int:chain_id>/', ChainView.as_view(), name='view_chain'),
    path('<int:chain_id>/target/<int:pk>/', ChainedTargetDetailView.as_view(), name='chain_target'),
    path('<int:chain_id>/<str:facility>/create/', SingleObservationCreateView.as_view(), name='create'),
]
