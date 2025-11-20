from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from chained.models import TemplatedChain
from tom_observations.models import ObservationTemplate
from tom_targets.models import Target


class AlertStreams(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    topic = models.CharField(max_length=255)
    automatic_observability = models.BooleanField(default=False)
    template_chained = models.ForeignKey(
        TemplatedChain, on_delete=models.PROTECT, null=True, blank=True
    )
    template_observation = models.ForeignKey(
        ObservationTemplate, on_delete=models.PROTECT, null=True, blank=True
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def clean(self):
        if self.topic not in settings.TOPICS:
            raise ValidationError(f"{self.topic} is not a valid topic.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class TargetStream(models.Model):
    target = models.OneToOneField(
        Target, on_delete=models.CASCADE, related_name="stream"
    )
    stream = models.CharField(max_length=255)

    def clean(self):
        if self.stream not in settings.TOPICS:
            raise ValidationError(f"{self.stream} is not a valid stream.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
