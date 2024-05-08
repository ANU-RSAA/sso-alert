from django.http import Http404
from django.shortcuts import render

from django.views.generic import TemplateView
from tom_observations.models import Target


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        return {"targets": Target.objects.all()}


def page_not_found(request, exception=None):
    return render(request, '404.html', status=404)
