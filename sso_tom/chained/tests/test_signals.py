from datetime import datetime

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
        target = Target.objects.create(
            name="Test Target",
            ra=20.3389,
            dec=31.5045,
        )
        user = User.objects.create(username="testuser")

        facility = "DREAMS"
        other_facility = "ANU 2.3m"
        parameters = {"param": "param1"}

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

        anu_230cm_parameters = {"cadence_strategy": "", "facility": "ANU 2.3m", "target_id": 4,
                                "observation_type": "OBSERVATION", "proposal": "456",
                                "userdefid": datetime.now().isoformat(), "userdefpri": 0, "nobsblk": 1, "maxseeing": "",
                                "photometric": False, "maxlunarphase": 100, "timeconstraint": "Flexible", "timeref": "",
                                "timewindow": None, "instr_pri_0": "WiFeS", "imgtype_0": "Object",
                                "mode_0": "ClassicalEqual", "dichroic_0": "RT480", "red_grating_0": "R3000",
                                "blue_grating_0": "B3000", "aperturewheel_0": "Clear", "ra_0": "20.3389",
                                "dec_0": "31.5045", "pmot_0": "0 0", "acq_ra_0": "", "acq_dec_0": "",
                                "acq_pmot_0": "", "blindacq_0": False, "rot_0": "PA", "rotang_0": 0.0, "mag_0": None,
                                "agfilter_0": "No Change", "guide_0": "BestEffort", "nexp_0": 1, "stellar_0": "false",
                                "binx_0": "1", "biny_0": "2", "exptime_0": 150, "sky_exptime_0": None, "scdescr_0": "",
                                "skya_ra_0": "", "skya_dec_0": ""}

        chained_observation2 = ChainedObservation.objects.create(
            chain=chain,
            facility=other_facility,
            parameters=anu_230cm_parameters,
        )

        chained_observation3 = ChainedObservation.objects.create(
            chain=chain,
            facility="Should not be triggered",
            parameters=parameters,
        )

        observation.status = 'Succeeded'
        observation.save()

        chained_observation2.refresh_from_db()

        self.assertTrue(chained_observation2.observation is not None)
        self.assertTrue(chained_observation3.observation is None)
