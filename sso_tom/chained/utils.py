import logging

from tom_observations.facility import get_service_class
from tom_observations.models import ObservationRecord

from sso_tom.utils import submit_to_facility

from .models import Chain, ChainedObservation

logger = logging.getLogger(__name__)


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
