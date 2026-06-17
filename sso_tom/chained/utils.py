import logging

from django.shortcuts import get_list_or_404, redirect
from tom_observations.facility import get_service_class
from tom_observations.models import ObservationRecord

from sso_tom.utils import submit_to_facility

from .models import Chain, ChainedObservation

logger = logging.getLogger(__name__)


def delete_chain(chain):
    if chain.status == Chain.DRAFT:
        chain.delete()
        return redirect("chains:chain_list")

    get_chained_observations_from_chain = (
        ChainedObservation.objects.select_related().filter(chain_id=chain.id)
    )

    for chained_observation in get_chained_observations_from_chain:
        if chained_observation.observation is None:
            # chained_observation.delete() # Shouldn't be needed because should cascade.
            continue

        facility = get_service_class(chained_observation.facility)()

        # Get facility terminal state.
        facility_terminal_states = facility.get_terminal_observing_states()
        # Get observation status.
        chained_observation_status = chained_observation.observation.status

        # If not in terminal state, cancel observation.
        if chained_observation_status not in facility_terminal_states:
            observation_id = chained_observation.observation.observation_id

            # First do another check on the observation status.
            state = facility.get_observation_status(observation_id)
            current_observation_state = state.get("state")

            if current_observation_state not in facility_terminal_states:
                facility.cancel_observation(observation_id)
                chained_observation.delete()

    # Check if any observations remaining. If yes, they are in terminal state. Do not delete.
    # If no, set to "DRAFT" and delete.
    remaining_observations = ChainedObservation.objects.get(chain_id=chain.id)
    if remaining_observations is None:
        chain.status = Chain.DRAFT
    else:
        chain.status = Chain.COMPLETED

    chain.save()

    if chain.status == Chain.DRAFT:
        chain.delete()

    return redirect("chains:chain_list")


def submit_chain(chain):
    first_chained_observation = (
        chain.chained_observations.filter(observation=None).order_by("created").first()
    )

    if first_chained_observation:
        facility = get_service_class(first_chained_observation.facility)()

        observation_ids, params = submit_to_facility(
            facility, first_chained_observation.parameters, chain.target
        )

        # Create Observation record
        record = ObservationRecord.objects.create(
            target=chain.target,
            user=chain.user,
            facility=facility.name,
            parameters=params,
            observation_id=observation_ids[0],
        )

        first_chained_observation.observation = record
        first_chained_observation.save()

        chain.status = Chain.SUBMITTED
    else:
        chain.status = Chain.COMPLETED

    chain.save()


def create_chain_and_submit_first(target, template_chained, user, topic=None):
    chain = Chain.objects.create(
        target=target,
        user=user,
        name=f"{target.name}_FROM_STREAM",
        description=f"{target.name}_FROM_STREAM. Retrieved as part of the topic = {topic}",
    )

    chained_templates = template_chained.chained_templates.all().order_by("created")

    for chained_template in chained_templates:
        ChainedObservation.objects.create(
            chain=chain,
            facility=chained_template.facility,
            parameters=chained_template.parameters,
            trigger_next_condition=chained_template.trigger_next_condition,
        )

    submit_chain(chain)
