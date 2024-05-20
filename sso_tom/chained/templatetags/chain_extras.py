from django import template, forms
from tom_observations.facility import get_service_classes

from ..forms import ChainedApplyObservationTemplateForm

register = template.Library()


# @register.inclusion_tag('tom_observations/partials/observationtemplate_run.html')
# def chain_observationtemplate_run(target):
#     """
#     Renders the form for running an observation template.
#     """
#     form = ChainedApplyObservationTemplateForm(initial={'target': target})
#     form.fields['chain'].widget = forms.HiddenInput()
#     form.fields['target'].widget = forms.HiddenInput()
#     return {'form': form}

@register.inclusion_tag('chained/partials/observing_buttons.html')
def chain_observing_buttons(target, chain_id):
    """
    Displays the observation buttons for all facilities available in the TOM.
    """
    facilities = get_service_classes()
    return {'target': target, 'facilities': facilities, 'chain_id': chain_id}


@register.filter
def get_dict_item(dictionary, key):
    return dictionary.get(key)
