import uuid

import logging

import requests
from decouple import config
from tom_observations.facility import get_service_class
from tom_observations.models import ObservationRecord

from .models import ChainedObservation, Chain
from sso_tom.utils import submit_to_facility

logger = logging.getLogger(__name__)

ADACS_PROPOSALDB_TEST_PASSWORD = config('ADACS_PROPOSALDB_TEST_PASSWORD')
ADACS_PROPOSALDB_TEST_USERNAME = config('ADACS_PROPOSALDB_TEST_USERNAME')
print(f"TOKENS FOR ACCESS {ADACS_PROPOSALDB_TEST_PASSWORD} {ADACS_PROPOSALDB_TEST_USERNAME}")


def submit_chain(chain):
    chained_observations = ChainedObservation.objects.filter(chain=chain).order_by('created')

    if chained_observations.exists():
        first_chained_observation = chained_observations.first()

        facility = get_service_class(first_chained_observation.facility)()

        observation_ids, params = submit_to_facility(facility, first_chained_observation.parameters, chain.target)

        # Create Observation record
        record = ObservationRecord.objects.create(
            target=chain.target,
            user=chain.user,
            facility=facility.name,
            parameters=params,
            observation_id=observation_ids[0]
        )

        first_chained_observation.observation = record
        first_chained_observation.save()

        chain.status = Chain.SUBMITTED
        chain.save()


def create_chain_and_submit_first(target, template_chained, user, topic=None):
    chain = Chain.objects.create(
        target=target,
        user=user,
        name=f'{target.name}_FROM_STREAM',
        description=f'{target.name}_FROM_STREAM. Retrieved as part of the topic = {topic}'
    )

    chained_templates = template_chained.chained_templates.all().order_by('created')

    for chained_template in chained_templates:
        ChainedObservation.objects.create(
            chain=chain,
            facility=chained_template.facility,
            parameters=chained_template.parameters,
            trigger_next_condition=chained_template.trigger_next_condition,
        )

    submit_chain(chain)
