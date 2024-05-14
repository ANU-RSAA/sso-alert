from datetime import datetime

from tom_observations.facility import get_service_class
from tom_observations.models import ObservationRecord

from tom_targets.templatetags.targets_extras import deg_to_sexigesimal


def submit_to_facility(facility, parameters, target):
    observation_ids = []

    now = datetime.now().strftime("%Y%m%dT%H%M%S")

    if facility.name == 'ANU 2.3m':
        parameters['userdefid'] = f"{parameters['userdefid']}_{target.name}_{now}"
        parameters['ra_0'] = deg_to_sexigesimal(target.ra, "hms")
        parameters['dec_0'] = deg_to_sexigesimal(target.dec, "dms")

        observation_ids = facility.submit_observation({
            'target': target,
            'params': parameters,
        })

    elif facility.name == 'DREAMS':
        parameters['user_defined_id'] = f"{now}_{parameters.get('proposal')}_{target.name}"
        parameters['ra'] = target.ra
        parameters['dec'] = target.dec

        observation_ids = facility.submit_observation(parameters)

    return observation_ids, parameters


def submit_observation_from_template(target, template, user):

    facility = get_service_class(template.facility)()

    parameters = template.parameters

    observation_ids, params = submit_to_facility(facility, parameters, target)

    # Create Observation record
    for observation_id in observation_ids:
        record = ObservationRecord.objects.create(
            target=target,
            user=user,
            facility=facility.name,
            parameters=params,
            observation_id=observation_id,
        )
