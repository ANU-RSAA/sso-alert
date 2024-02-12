from django.shortcuts import render

from django.views.generic import TemplateView
from tom_observations.models import Target


class AboutView(TemplateView):
    template_name = "fink_ui/about.html"

    def get_context_data(self, **kwargs):
        return {"targets": Target.objects.all()}
