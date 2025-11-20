# from django.forms import forms
from crispy_forms.layout import Field, Submit, Layout
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from guardian.mixins import LoginRequiredMixin
from tom_observations.models import ObservationTemplate

from .models import AlertStreams
from .forms import AlertStreamsForm
from chained.models import TemplatedChain


@login_required
def toggle_active(request, pk):
    alert_stream = get_object_or_404(AlertStreams, pk=pk, user=request.user)
    alert_stream.active = not alert_stream.active
    alert_stream.save()
    return redirect("sso_alerts:alert_list")


class AlertListView(LoginRequiredMixin, ListView):
    template_name = "sso_alerts/alerts_list.html"
    model = AlertStreams

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class AlertStreamsCreateView(LoginRequiredMixin, CreateView):
    model = AlertStreams
    form_class = AlertStreamsForm
    template_name = "sso_alerts/alert_streams_form.html"
    success_url = reverse_lazy("sso_alerts:alert_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["template_chained"].queryset = TemplatedChain.objects.filter(
            user=self.request.user, status=TemplatedChain.FINALIZED
        )
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AlertStreamsUpdateView(LoginRequiredMixin, UpdateView):
    model = AlertStreams
    form_class = AlertStreamsForm
    template_name = "sso_alerts/alert_streams_form.html"
    success_url = reverse_lazy("sso_alerts:alert_list")

    def get_object(self, queryset=None):
        """
        Override get_object to ensure the user can only update their own AlertStreams.
        """
        obj = get_object_or_404(
            AlertStreams, pk=self.kwargs["pk"], user=self.request.user
        )
        return obj

    def get_form(self, form_class=None):
        """
        Override get_form to filter the 'template_chained' queryset to only include
        finalized TemplatedChain objects that belong to the logged-in user.
        """
        form = super().get_form(form_class)
        form.fields["template_chained"].queryset = TemplatedChain.objects.filter(
            user=self.request.user, status=TemplatedChain.FINALIZED
        )
        # Add the 'active' field for the update form
        form.fields["active"] = forms.BooleanField(
            initial=self.object.active, required=False
        )

        # Set initial value for 'template_type'
        if self.object.template_chained:
            form.fields["template_type"].initial = "Chain"
        elif self.object.template_observation:
            form.fields["template_type"].initial = "Single"
        else:
            form.fields["template_type"].initial = None

        # Disable some fields so that these cannot be modified
        form.fields["topic"].disabled = True
        form.fields["automatic_observability"].disabled = True
        form.fields["template_type"].disabled = True
        form.fields["template_chained"].disabled = True
        form.fields["template_observation"].disabled = True

        # Adjust the layout to place the 'active' field
        form.helper.layout = Layout(
            "name",
            "description",
            "topic",
            "automatic_observability",
            Field("template_type", css_class="form-group hidden-field"),
            "template_chained",
            "template_observation",
            Field("active", css_class="form-check"),
            Submit("submit", "Submit"),
        )

        return form

    def form_valid(self, form):
        """
        Override form_valid to ensure the user is set correctly on the form instance.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)
