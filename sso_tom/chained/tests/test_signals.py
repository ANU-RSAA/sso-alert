from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.

from tom_observations.models import ObservationRecord
from chained.models import ChainedObservation, Chain
from tom_targets.models import Target


class ObservationRecordSignalTestCase(TestCase):

    def test_observation_record_created_signal(self):
        """
        Test that the signal is triggered when an ObservationRecord is created.
        """
        target = Target.objects.create(name="Test Target")
        user = User.objects.create(username="testuser")
        observation = ObservationRecord.objects.create(
            target=target,
            user=user,
            facility="Test Facility",
            parameters={"param1": "value1"},
            observation_id="obs1",
            status="NEW",
            scheduled_start=None,
            scheduled_end=None,
        )

        self.assertTrue(observation.pk is not None)

    def test_observation_record_updated_signal(self):
        """
        Test that the signal is triggered when an ObservationRecord is updated.
        """
        target = Target.objects.create(name="Test Target")
        user = User.objects.create(username="testuser")

        facility = "Test Facility"
        other_facility = "Other Facility"
        parameters = {"param1": "value1"}

        chain = Chain.objects.create(
            name="Test Chain",
            target=target,
            user=user,
        )

        observation = ObservationRecord.objects.create(
            target=target,
            user=user,
            facility=facility,
            parameters=parameters,
            observation_id="obs1",
            status="Pending",
            scheduled_start=None,
            scheduled_end=None,
        )

        chained_observation = ChainedObservation.objects.create(
            chain=chain,
            observation=observation,
            facility=facility,
            parameters=parameters,
            trigger_next_condition=['Succeeded', 'Detected']
        )

        chained_observation2 = ChainedObservation.objects.create(
            chain=chain,
            facility=other_facility,
            parameters=parameters,
        )

        chained_observation2 = ChainedObservation.objects.create(
            chain=chain,
            facility="Should not be triggered",
            parameters=parameters,
        )

        observation.status = 'Succeeded'
        observation.save()
