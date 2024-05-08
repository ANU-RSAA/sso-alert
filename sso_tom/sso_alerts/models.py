from django.contrib.auth import get_user_model
from django.db import models

from chained.models import TemplatedChain
from tom_observations.models import ObservationTemplate


class AlertStreams(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    topic = models.CharField(max_length=255)
    automatic_observability = models.BooleanField(default=False)
    template_chained = models.ForeignKey(TemplatedChain, on_delete=models.PROTECT, null=True, blank=True)
    template_observation = models.ForeignKey(ObservationTemplate, on_delete=models.PROTECT, null=True, blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

