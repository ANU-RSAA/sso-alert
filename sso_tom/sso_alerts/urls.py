from django.urls import path, include

from .views import (
    AlertListView,
    AlertStreamsCreateView
)

app_name = 'sso_alerts'

urlpatterns = [
    path('', AlertListView.as_view(), name='alert_list'),
    path('create/', AlertStreamsCreateView.as_view(), name='alert_streams_create'),

]
