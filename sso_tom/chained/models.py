from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
from tom_observations.cadence import BaseCadenceForm, CadenceStrategy
from tom_alerts.alerts import GenericAlert, GenericBroker, GenericQueryForm
from tom_alerts.models import BrokerQuery
from datetime import datetime, timedelta
from dateutil.parser import parse
import logging
import traceback

from tom_observations.models import ObservationRecord, ObservationTemplate
from tom_observations.facility import get_service_class

from tom_observations.cadence import get_cadence_strategy
from tom_observations.models import DynamicCadence
from tom_targets.models import Target

logger = logging.getLogger(__name__)


class SsoAlertCadenceForm(BaseCadenceForm):
    pass


class SsoAlertCadenceStrategy(CadenceStrategy):
    """The ResumeCadenceAfterFailureStrategy chooses when to submit the next observation based on the success of the
    previous observation. If the observation is successful, it submits a new one on the same cadence--that is, if the
    cadence is every three days, it will submit the next observation three days in the future. If the observations
    fails, it will submit the next observation immediately, and follow the same decision tree based on the success
    of the subsequent observation.

    In order to properly subclass this CadenceStrategy, one should override ``update_observation_payload``.

    This strategy requires the DynamicCadence to have a parameter ``cadence_frequency``."""

    name = 'SSO_ALERT_MULTI_FACILITY_CADENCE'
    description = """This strategy schedules one observation in the cadence at a time. If the observation fails, it
                     re-submits the observation until it succeeds. If it succeeds, it submits the next observation on
                     the same cadence."""
    form = SsoAlertCadenceForm

    def update_observation_payload(self, observation_payload):
        """
        :param observation_payload: form parameters for facility observation form
        :type observation_payload: dict
        """
        return observation_payload

    def run(self):
        print(f"RUN CADENCE STRATEGY FOR SSO_ALERT")
        # Obtain list of "Broker Query" entries. I think we will only support the "Fink" query broker.
        # gets the most recent observation because the next observation is just going to modify these parameters
        broker_queries = BrokerQuery.objects.all()
        for broker_query in broker_queries:
            print(f" Broker Query={broker_query}")
        # Lets just assume for the moment that none of the "Broker Queries" have come up with new observations
        # We want to iterate through every currently submitted observation we are responsible for.  For now that will only involve the
        # ANU230cm facility but soon it will also include the DREAMS facility (and one day the GOTO facility)
        observations_we_are_responsible_for = ObservationRecord.objects.filter(facility="ANU 2.3m").exclude(
            status="").exclude(status="Complete")
        for observation in observations_we_are_responsible_for:
            print(
                f"  was Observation {observation} with id={observation.observation_id} status={observation.status} terminal={observation.terminal}")
            facility = get_service_class(observation.facility)()
            facility.update_observation_status(observation.observation_id)  # Updates the DB record
            observation.refresh_from_db()
            print(
                f"  is Observation {observation} with id={observation.observation_id} status={observation.status} terminal={observation.terminal}")

        # Creation of corresponding ObservationRecord objects for the observations
        new_observations = []

        return new_observations

    def runorig(self):
        print(f"RUN CADENCE STRATEGY FOR SSO_ALERT")
        # gets the most recent observation because the next observation is just going to modify these parameters
        last_obs = self.dynamic_cadence.observation_group.observation_records.order_by('-created').first()

        # Make a call to the facility to get the current status of the observation
        facility = get_service_class(last_obs.facility)()
        facility.update_observation_status(last_obs.observation_id)  # Updates the DB record
        last_obs.refresh_from_db()  # Gets the record updates

        # Boilerplate to get necessary properties for future calls
        start_keyword, end_keyword = facility.get_start_end_keywords()
        observation_payload = last_obs.parameters

        # Cadence logic
        # If the observation hasn't finished, do nothing
        if not last_obs.terminal:
            return
        elif last_obs.failed:  # If the observation failed
            # Submit next observation to be taken as soon as possible with the same window length
            window_length = parse(observation_payload[end_keyword]) - parse(observation_payload[start_keyword])
            observation_payload[start_keyword] = datetime.now().isoformat()
            observation_payload[end_keyword] = (parse(observation_payload[start_keyword]) + window_length).isoformat()
        else:  # If the observation succeeded
            # Advance window normally according to cadence parameters
            observation_payload = self.advance_window(
                observation_payload, start_keyword=start_keyword, end_keyword=end_keyword
            )

        observation_payload = self.update_observation_payload(observation_payload)

        # Submission of the new observation to the facility
        obs_type = last_obs.parameters.get('observation_type')
        form = facility.get_form(obs_type)(data=observation_payload)
        if form.is_valid():
            observation_ids = facility.submit_observation(form.observation_payload())
        else:
            logger.error(msg=f'Unable to submit next cadenced observation: {form.errors}')
            raise Exception(f'Unable to submit next cadenced observation: {form.errors}')

        # Creation of corresponding ObservationRecord objects for the observations
        new_observations = []
        for observation_id in observation_ids:
            # Create Observation record
            record = ObservationRecord.objects.create(
                target=last_obs.target,
                facility=facility.name,
                parameters=observation_payload,
                observation_id=observation_id
            )
            # Add ObservationRecords to the DynamicCadence
            self.dynamic_cadence.observation_group.observation_records.add(record)
            self.dynamic_cadence.observation_group.save()
            new_observations.append(record)

        # Update the status of the ObservationRecords in the DB
        for obsr in new_observations:
            facility = get_service_class(obsr.facility)()
            facility.update_observation_status(obsr.observation_id)

        return new_observations

    def advance_window(self, observation_payload, start_keyword='start', end_keyword='end'):
        cadence_frequency = self.dynamic_cadence.cadence_parameters.get('cadence_frequency')
        if not cadence_frequency:
            raise Exception(f'The {self.name} strategy requires a cadence_frequency cadence_parameter.')
        advance_window_hours = cadence_frequency
        window_length = parse(observation_payload[end_keyword]) - parse(observation_payload[start_keyword])

        new_start = parse(observation_payload[start_keyword]) + timedelta(hours=advance_window_hours)
        if new_start < datetime.now():  # Ensure that the new window isn't in the past
            new_start = datetime.now()
        new_end = new_start + window_length
        observation_payload[start_keyword] = new_start.isoformat()
        observation_payload[end_keyword] = new_end.isoformat()

        return observation_payload


class Chain(models.Model):
    DRAFT = 'DRAFT'
    SUBMITTED = 'SUBMITTED'
    COMPLETED = 'COMPLETED'

    CHAIN_STATUS = (
        (DRAFT, DRAFT),
        (SUBMITTED, SUBMITTED),
        (COMPLETED, COMPLETED),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    target = models.ForeignKey(Target, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(choices=CHAIN_STATUS, max_length=20, default=DRAFT)


class ChainedObservation(models.Model):

    FAILED = 'FAILED'
    REJECTED = 'REJECTED'
    COMPLETED = 'COMPLETED'

    CONDITION_CHOICES = (
        (FAILED, FAILED),
        (REJECTED, REJECTED),
        (COMPLETED, COMPLETED),
    )

    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)
    facility = models.CharField(max_length=50)
    parameters = models.JSONField()
    observation = models.ForeignKey(ObservationRecord, on_delete=models.CASCADE, null=True, blank=True)
    trigger_next_condition = models.CharField(choices=CONDITION_CHOICES, max_length=20, default=FAILED)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "NOT SUBMITTED" if not self.observation else "SUBMITTED"
        return f'{self.facility} ({status})'


class TemplatedChain(models.Model):
    DRAFT = 'DRAFT'
    FINALIZED = 'FINALIZED'

    TEMPLATED_CHAIN_STATUS = (
        (DRAFT, DRAFT),
        (FINALIZED, FINALIZED),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=TEMPLATED_CHAIN_STATUS, max_length=20, default=DRAFT)

    def __str__(self):
        return self.name


class ChainedTemplate(models.Model):
    FAILED = 'FAILED'
    REJECTED = 'REJECTED'
    COMPLETED = 'COMPLETED'

    CONDITION_CHOICES = (
        (FAILED, FAILED),
        (REJECTED, REJECTED),
        (COMPLETED, COMPLETED),
    )

    templated_chain = models.ForeignKey(TemplatedChain, on_delete=models.CASCADE, related_name='chained_templates')
    name = models.CharField(max_length=255)
    facility = models.CharField(max_length=50)
    parameters = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)
    trigger_next_condition = models.CharField(choices=CONDITION_CHOICES, max_length=20, default=FAILED)

    def __str__(self):
        return f'{self.facility} ({self.templated_chain})'
