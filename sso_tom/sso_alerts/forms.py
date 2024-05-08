from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset, Layout, Field, HTML
from django import forms
from django.utils.safestring import mark_safe

from .models import AlertStreams


class AlertStreamsForm(forms.ModelForm):
    TEMPLATE_TYPE_CHOICES = (
        ('Chain', 'Chain'),
        ('Single', 'Single Observation'),
    )

    template_type = forms.ChoiceField(choices=TEMPLATE_TYPE_CHOICES, label='Template Type')

    class Meta:
        model = AlertStreams
        exclude = ['user', 'created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['topic'].label = mark_safe('Topic (<small>For available topics, please refer to: <a href="https://fink-broker.readthedocs.io/en/latest/science/filters/#available-topics">Available Topics</a></small>)')
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            'name',
            'description',
            'topic',
            'automatic_observability',
            Field('template_type', css_class='form-group hidden-field'),
            'template_chained',
            'template_observation',
            Submit('submit', 'Submit'),
        )

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if user:
            instance.user = user
        if commit:
            instance.save()
        return instance
