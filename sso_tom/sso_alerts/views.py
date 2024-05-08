from django.shortcuts import render
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy

from .models import AlertStreams
from .forms import AlertStreamsForm


class AlertListView(ListView):
    template_name = 'sso_alerts/alerts_list.html'
    model = AlertStreams

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class AlertStreamsCreateView(CreateView):
    model = AlertStreams
    form_class = AlertStreamsForm
    template_name = 'sso_alerts/alert_streams_form.html'
    success_url = reverse_lazy('sso_alerts:alert_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)



