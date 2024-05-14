from django.shortcuts import render
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from guardian.mixins import LoginRequiredMixin
from tom_observations.models import ObservationTemplate

from .models import AlertStreams
from .forms import AlertStreamsForm
from chained.models import TemplatedChain


class AlertListView(LoginRequiredMixin, ListView):
    template_name = 'sso_alerts/alerts_list.html'
    model = AlertStreams

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class AlertStreamsCreateView(LoginRequiredMixin, CreateView):
    model = AlertStreams
    form_class = AlertStreamsForm
    template_name = 'sso_alerts/alert_streams_form.html'
    success_url = reverse_lazy('sso_alerts:alert_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['template_chained'].queryset = TemplatedChain.objects.filter(user=self.request.user,
                                                                                 status=TemplatedChain.FINALIZED)
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
