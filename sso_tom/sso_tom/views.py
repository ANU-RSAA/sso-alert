from django.http import Http404
from django.shortcuts import render

from django.views.generic import TemplateView
from tom_observations.models import Target
from tom_observations.views import ObservationCreateView, ObservationTemplateCreateView, ObservationTemplateUpdateView


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        return {"targets": Target.objects.all()}


def page_not_found(request, exception=None):
    return render(request, '404.html', status=404)


class CustomObservationCreateView(ObservationCreateView):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        facility = self.get_facility_class()()
        if facility.name == 'ANU 2.3m':
            # Pass request.user to the form
            kwargs['user'] = self.request.user
        return kwargs


class CustomObservationTemplateCreateView(ObservationTemplateCreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            facility = self.request.POST.get('facility')
            if facility == 'ANU 2.3m':
                # Pass request.user to the form
                kwargs['user'] = self.request.user
        return kwargs


class CustomObservationTemplateUpdateView(ObservationTemplateUpdateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        facility = self.request.POST.get('facility')
        if facility == 'ANU 2.3m':
            # Pass request.user to the form
            kwargs['user'] = self.request.user
        return kwargs
