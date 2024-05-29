from django.urls import path, include

from .views import (
    AlertListView,
    AlertStreamsCreateView,
    AlertStreamsUpdateView,
    toggle_active,
)

app_name = 'sso_alerts'

urlpatterns = [
    path('', AlertListView.as_view(), name='alert_list'),
    path('create/', AlertStreamsCreateView.as_view(), name='alert_streams_create'),
    path('update/<int:pk>/', AlertStreamsUpdateView.as_view(), name='alert_streams_update'),
    path('toggle_active/<int:pk>/', toggle_active, name='toggle_active'),
]
