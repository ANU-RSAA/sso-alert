import json
import logging
from datetime import timedelta
from types import SimpleNamespace

import requests
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Div, Fieldset, Layout, Submit
from django import forms
from django.conf import settings
from django.utils import timezone
from tom_observations.facility import (
    BaseRoboticObservationFacility,
    BaseRoboticObservationForm,
)
from tom_observations.models import ObservationRecord
from tom_observations.observation_template import GenericTemplateForm
from tom_targets.models import Target

# Code to select a blank sky - CLi
from sso_tom.selectSky import selectSky

logger = logging.getLogger(__name__)

CHOICES = {
    "TIMECONSTRAINT": [
        ("Flexible", "Flexible"),
        ("Fixed", "Fixed"),
    ],
    "MODE": [
        ("ClassicalEqual", "Classical Equal"),
        ("ObjectSkyNodAndShuffle", "Object Sky Nod And Shuffle"),
    ],
    "DICHROIC": [
        # Put RT50 first
        ("RT560", "RT560"),
        ("RT480", "RT480"),
        ("RT615", "RT615"),
    ],
    "RED_GRATING": [
        ("R3000", "R3000"),
        ("R7000", "R7000"),
        ("I7000", "I7000"),
    ],
    "BLUE_GRATING": [
        ("B3000", "B3000"),
        ("B7000", "B7000"),
        ("U7000", "U7000"),
    ],
    "ROT": [
        ("PA", "Position Angle"),
        ("VA", "Vert. Angle (init)"),
    ],
    "AGFILTER": [
        ("B", "B"),
        ("V", "V"),
        ("R", "R"),
        ("I", "I"),
        ("ND", "ND"),
    ],
    "GUIDE": [
        ("No", "No"),
        ("BestEffort", "Best Effort"),
        ("AcqStar", "Acquire Star"),
    ],
    "STELLAR": [
        ("true", "Stellar"),
        ("false", "Full Field"),
    ],
    "BINX": [
        (1, "1"),
        (2, "2"),
    ],
    "BINY": [
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
    ],
}


def is_valid_proposal(proposal, user):
    url = settings.ANU_SITE + "propusers.php"
    response = requests.get(
        url,
        params={"PROPOSAL": proposal},
        auth=(settings.PROPOSAL_DB_USERNAME, settings.PROPOSAL_DB_PASSWORD),
    )

    try:
        content = json.loads(response.content.decode())
        if content["status"] and content["auth"] and content["found"]:
            for member in content.get("member", []):
                if member["user"] == user.email and member["featureBits"] & 1:
                    return True, ""
            return (
                False,
                f"You ({user.email}) are not authorized for proposal: {proposal}",
            )
        else:
            return False, content["msg"].replace("alertproxy", "The system")
    except Exception:
        return (
            False,
            f"The system cannot check the proposal id {proposal} (make sure it is valid)",
        )


# Class that displays a GUI form for users to create an observation.
class ANU230cmForm(BaseRoboticObservationForm):
    proposal = forms.CharField(
        label="Proposal ID",
    )
    userdefid = forms.CharField(
        label="User Def. ID",
    )
    userdefpri = forms.IntegerField(
        label="User Def. Priority",
        initial=0,
    )
    nobsblk = forms.IntegerField(
        label="No. Obs. Blocks",
        initial=1,
        disabled=True,
    )
    maxseeing = forms.CharField(
        label='Max Seeing (")',
        required=False,
    )

    maxlunarphase = forms.IntegerField(
        label="Max. Lunar Phase (%)",
        required=False,
        initial=100,
    )

    maxlunarphase = forms.IntegerField(
        label="Max. Lunar Phase (%)",
        required=False,
        initial=100,
    )
    # Renamed to sky transpareny
    skytransparency = forms.BooleanField(
        label="Clear conditions",
        required=False,
    )
    # CLi Added lunar distance
    minlunardist = forms.IntegerField(
        label="Min. Lunar distance (degrees)",
        required=False,
        initial=30,
    )
    timeconstraint = forms.ChoiceField(
        label="Time Constraint",
        required=False,
        initial="Flexible",
        choices=CHOICES["TIMECONSTRAINT"],
    )
    timeref = forms.CharField(
        label="Time Ref. (UTC)",
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime"}, format="%Y-%m-%d %H:%M:%S"
        ),
    )  # YYYY-MM-DD hh:mm:ss
    timewindow = forms.IntegerField(
        label="Time Window",
        required=False,
    )
    instr_pri_0 = forms.CharField(
        label="Primary Instrument",
        initial="WiFeS",
        disabled=True,
    )
    imgtype_0 = forms.CharField(
        label="Image Type",
        initial="Object",
        disabled=True,
    )
    mode_0 = forms.ChoiceField(
        label="Mode",
        initial="ClassicalEqual",
        choices=CHOICES["MODE"],
    )
    dichroic_0 = forms.ChoiceField(
        label="Dichroic",
        choices=CHOICES["DICHROIC"],
    )
    red_grating_0 = forms.ChoiceField(
        label="Red Grating",
        choices=CHOICES["RED_GRATING"],
    )
    blue_grating_0 = forms.ChoiceField(
        label="Blue Grating",
        choices=CHOICES["BLUE_GRATING"],
    )
    aperturewheel_0 = forms.CharField(
        label="Aperture Wheel",
        required=False,
        initial="Clear",
        disabled=True,
    )
    ra_0 = forms.CharField(
        label="RA",
        required=False,
        disabled=True,
    )
    dec_0 = forms.CharField(
        label="Dec",
        required=False,
        disabled=True,
    )
    pmot_0 = forms.CharField(
        label="Prop. Motion",
        required=False,
        # initial="0 0",
        disabled=True,
    )
    acq_ra_0 = forms.CharField(
        label="Acquired RA",
        required=False,
    )
    acq_dec_0 = forms.CharField(
        label="Acquired Dec",
        required=False,
    )
    acq_pmot_0 = forms.CharField(
        label="Acq. Prop. Motion",
        required=False,
    )
    blindacq_0 = forms.BooleanField(
        label="Blind Acquisition",
        required=False,
        initial=False,
    )
    rot_0 = forms.ChoiceField(
        label="Rotator Mode", initial="PA", choices=CHOICES["ROT"]
    )
    rotang_0 = forms.FloatField(
        label="Rotation Angle",
        required=False,
        initial=0.0,
    )
    mag_0 = forms.FloatField(
        label="Magnitude",
        required=False,
    )
    agfilter_0 = forms.ChoiceField(
        label="A&G Filter",
        required=False,
        initial="R",
        choices=CHOICES["AGFILTER"],
    )
    guide_0 = forms.ChoiceField(
        label="Guiding",
        required=False,
        initial="BestEffort",
        choices=CHOICES["GUIDE"],
    )
    nexp_0 = forms.IntegerField(
        label="Num. Exposures",
        required=False,
        initial=1,
    )
    stellar_0 = forms.ChoiceField(
        label="Region of Interest",
        required=False,
        initial="false",
        choices=CHOICES["STELLAR"],
    )
    binx_0 = forms.ChoiceField(
        label="Spectral Binning",
        required=False,
        initial=1,
        choices=CHOICES["BINX"],
    )
    biny_0 = forms.ChoiceField(
        label="Spatial Binning",
        required=False,
        initial=2,
        choices=CHOICES["BINY"],
    )
    exptime_0 = forms.IntegerField(
        label="Exposure time (s)",
        initial=150,
    )
    sky_exptime_0 = forms.IntegerField(
        label="Sky Exp. time (s)",
        required=False,
    )
    scdescr_0 = forms.CharField(
        label="Sub-cycle Description",
        required=False,
    )
    autoselsky_0 = forms.BooleanField(
        label="Automatic Selection",
        required=False,
        initial=False,
    )

    skya_ra_0 = forms.CharField(
        label="Sky A RA",
        required=False,
    )
    skya_dec_0 = forms.CharField(
        label="Sky A Dec",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            self.common_layout,
            self.layout(),
            self.button_layout(),
        )

    def is_valid(self):
        # Make this call the validate_observation method in facility
        valid = super().is_valid()

        if not valid:
            return valid

        if not self.cleaned_data.get("proposal"):
            self.add_error("proposal", "Proposal ID is required.")
            valid = False
        else:
            valid, message = is_valid_proposal(
                proposal=self.cleaned_data["proposal"], user=self.user
            )
            if not valid:
                self.add_error(None, message)

        return valid

    def layout(self):
        return Div(
            Fieldset(
                "Observation",
                Div(
                    Div("proposal", css_class="col"),
                    Div("userdefid", css_class="col"),
                    Div("userdefpri", css_class="col"),
                    css_class="form-row",
                ),
                Div(
                    Div("nobsblk", css_class="col"),
                    Div("instr_pri_0", css_class="col"),
                    Div("imgtype_0", css_class="col"),
                    css_class="form-row",
                ),
                Div(
                    Div("maxseeing", css_class="col"),
                    Div("skytransparency", css_class="col"),
                    css_class="form-row",
                ),
                Div(
                    Div("maxlunarphase", css_class="col"),
                    Div("minlunardist", css_class="col"),
                    css_class="form-row",
                ),
                Div(
                    Div("timeconstraint", css_class="col"),
                    Div("timeref", css_class="col"),
                    Div("timewindow", css_class="col"),
                    css_class="form-row",
                ),
                Div(Div("mode_0", css_class="col"), css_class="form-row"),
            ),
            Fieldset(
                "Instrument Configuration",
                Div(
                    Div("dichroic_0", css_class="col"),
                    Div("red_grating_0", css_class="col"),
                    Div("blue_grating_0", css_class="col"),
                    css_class="form-row",
                ),
                Div(Div("aperturewheel_0", css_class="col"), css_class="form-row"),
            ),
            Fieldset(
                "Exposure",
                Div(
                    Div("exptime_0", css_class="col"),
                    Div("sky_exptime_0", css_class="col"),
                    Div("nexp_0", css_class="col"),
                    css_class="form-row",
                ),
                Div(Div("stellar_0", css_class="col"), css_class="form-row"),
                Div(
                    Div("binx_0", css_class="col"),
                    Div("biny_0", css_class="col"),
                    css_class="form-row",
                ),
            ),
            # Sky and nodding sequence
            Fieldset(
                "Sky Position",
                Div(Div("autoselsky_0", css_class="col"), css_class="form-row"),
                Div(
                    Div("skya_ra_0", css_class="col"),
                    Div("skya_dec_0", css_class="col"),
                    css_class="form-row",
                ),
            ),
            Fieldset(
                "Nod sequence",
                Div(Div("scdescr_0", css_class="col"), css_class="form-row"),
            ),
            Fieldset(
                "Object, Acquisition & Guide",
                Div(
                    Div("ra_0", css_class="col"),
                    Div("dec_0", css_class="col"),
                    Div("pmot_0", css_class="col"),
                    css_class="form-row",
                ),
                Div(
                    Div("acq_ra_0", css_class="col"),
                    Div("acq_dec_0", css_class="col"),
                    Div("acq_pmot_0", css_class="col"),
                    css_class="form-row",
                ),
                Div(Div("blindacq_0", css_class="col"), css_class="form-row"),
                Div(
                    Div("rot_0", css_class="col"),
                    Div("rotang_0", css_class="col"),
                    css_class="form-row",
                ),
                Div(
                    Div("mag_0", css_class="col"),
                    Div("agfilter_0", css_class="col"),
                    Div("guide_0", css_class="col"),
                    css_class="form-row",
                ),
            ),
        )

    def button_layout(self):
        # target_id = self.initial.get('target_id')
        return ButtonHolder(
            Submit("submit", "Submit"),
            Submit("add_to_chain", "Add to Chain"),
        )

    def observation_payload(self):
        """
        This method is called to extract the data from the form into a dictionary that
        can be used by the rest of the module. In the base implementation it simply dumps
        the form into a json string.
        """
        from astropy import units
        from astropy.coordinates import Angle

        target = Target.objects.get(pk=self.cleaned_data["target_id"])

        # Convert ra/dec Target fields back to strings of correct format
        # and add them to Observation data.
        self.cleaned_data["ra_0"] = Angle(target.ra, unit=units.degree).to_string(
            unit=units.hourangle, sep=" "
        )
        self.cleaned_data["dec_0"] = Angle(target.dec, unit=units.degree).to_string(
            unit=units.degree, sep=" "
        )

        # Convert proper motion ra/dec Target fields into one string of correct format
        # and add them to Observation data.
        if target.pm_dec is None:
            pmot_dec = 0
        else:
            pmot_dec = target.pm_dec
        if target.pm_ra is None:
            pmot_ra = 0
        else:
            pmot_ra = target.pm_ra
        self.cleaned_data["pmot_0"] = f"{pmot_ra} {pmot_dec}"

        return {"target_id": target.id, "params": self.serialize_parameters()}


# Class that displays a GUI form for users to create an observation template.
class ANU230cmTemplateForm(GenericTemplateForm):
    proposal = forms.CharField(
        label="Proposal ID",
    )
    userdefid = forms.CharField(
        label="User Def. ID",
        required=False,
    )
    userdefpri = forms.IntegerField(
        label="User Def. Priority",
        initial=0,
        required=False,
    )
    nobsblk = forms.IntegerField(
        label="No. Obs. Blocks",
        initial=1,
        disabled=True,
        required=False,
    )
    maxseeing = forms.CharField(
        label='Max Seeing (")',
        required=False,
    )
    # Renamed to sky transpareny
    skytransparency = forms.BooleanField(
        label="Clear conditions",
        required=False,
    )
    maxlunarphase = forms.IntegerField(
        label="Max. Lunar Phase (%)",
        required=False,
        initial=100,
    )
    # CLi Added lunar distance
    minlunardist = forms.IntegerField(
        label="Min. Lunar distance (degrees)",
        required=False,
        initial=30,
    )
    timeconstraint = forms.ChoiceField(
        label="Time Constraint",
        required=False,
        choices=CHOICES["TIMECONSTRAINT"],
        initial="Flexible",
    )
    timeref = forms.DateTimeField(
        label="Time Ref. (UTC)",
        required=False,
    )
    timewindow = forms.IntegerField(
        label="Time Window",
        required=False,
    )
    instr_pri_0 = forms.CharField(
        label="Primary Instrument",
        required=False,
        initial="WiFeS",
        disabled=True,
    )
    imgtype_0 = forms.CharField(
        label="Image Type",
        required=False,
        initial="Object",
        disabled=True,
    )
    mode_0 = forms.ChoiceField(
        label="Mode",
        choices=CHOICES["MODE"],
        initial="ClassicalEqual",
        required=False,
    )
    dichroic_0 = forms.ChoiceField(
        label="Dichroic",
        choices=CHOICES["DICHROIC"],
        required=False,
    )
    red_grating_0 = forms.ChoiceField(
        label="Red Grating", choices=CHOICES["RED_GRATING"], required=False
    )
    blue_grating_0 = forms.ChoiceField(
        label="Blue Grating", choices=CHOICES["BLUE_GRATING"], required=False
    )
    aperturewheel_0 = forms.CharField(
        label="Aperture Wheel",
        required=False,
        initial="Clear",
        disabled=True,
    )
    ra_0 = forms.CharField(
        label="RA",
        required=False,
        disabled=True,
    )
    dec_0 = forms.CharField(
        label="Dec",
        required=False,
        disabled=True,
    )
    pmot_0 = forms.CharField(
        label="Prop. Motion",
        required=False,
        initial="0 0",
        disabled=True,
    )
    acq_ra_0 = forms.CharField(
        label="Acquired RA",
        required=False,
        disabled=True,
    )
    acq_dec_0 = forms.CharField(
        label="Acquired Dec",
        required=False,
        disabled=True,
    )
    acq_pmot_0 = forms.CharField(
        label="Acq. Prop. Motion",
        required=False,
        disabled=True,
    )
    blindacq_0 = forms.BooleanField(
        label="Blind Acquisition",
        required=False,
        initial=False,
    )
    # Added an automatic options
    autoselacqstar_0 = forms.BooleanField(
        label="Automatic Selection",
        required=False,
        initial=True,
    )
    autoselsky_0 = forms.BooleanField(
        label="Automatic Selection",
        required=False,
        initial=True,
    )
    rot_0 = forms.ChoiceField(
        label="Rotator Mode",
        choices=CHOICES["ROT"],
        initial="PA",
        required=False,
    )
    rotang_0 = forms.FloatField(
        label="Rotation Angle",
        required=False,
        initial=0.0,
    )
    mag_0 = forms.FloatField(
        label="Magnitude",
        required=False,
    )
    agfilter_0 = forms.ChoiceField(
        label="A&G Filter",
        required=False,
        choices=CHOICES["AGFILTER"],
        initial="R",
    )
    guide_0 = forms.ChoiceField(
        label="Guiding",
        required=False,
        choices=CHOICES["GUIDE"],
        initial="BestEffort",
    )
    nexp_0 = forms.IntegerField(
        label="Num. Exposures",
        required=False,
        initial=1,
    )
    stellar_0 = forms.ChoiceField(
        label="Region of Interest",
        required=False,
        choices=CHOICES["STELLAR"],
        initial="false",
    )
    binx_0 = forms.ChoiceField(
        label="Spectral Binning",
        required=False,
        choices=CHOICES["BINX"],
        initial=1,
    )
    biny_0 = forms.ChoiceField(
        label="Spatial Binning",
        required=False,
        choices=CHOICES["BINY"],
        initial=2,
    )
    exptime_0 = forms.IntegerField(
        label="Exposure time (s)",
        initial=150,
        required=False,
    )
    sky_exptime_0 = forms.IntegerField(
        label="Sky Exp. time (s)",
        required=False,
    )
    scdescr_0 = forms.CharField(
        label="Sub-cycle Description",
        required=False,
    )
    skya_ra_0 = forms.CharField(
        label="Sky A RA",
        required=False,
    )
    skya_dec_0 = forms.CharField(
        label="Sky A Dec",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)
        self.common_layout = Layout("facility", "template_name")
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))
        self.helper.layout = Layout(
            self.common_layout,
            self.layout(),
        )

    def is_valid(self):

        valid = super().is_valid()

        if not valid:
            return valid

        if not self.cleaned_data.get("proposal"):
            self.add_error("proposal", "Proposal ID is required.")
            valid = False
        else:
            valid, message = is_valid_proposal(
                proposal=self.cleaned_data["proposal"], user=self.user
            )
            if not valid:
                self.add_error(None, message)

        return valid

    def layout(self):
        return Div(
            Fieldset(
                "Observation",
                Div(
                    Div("proposal", css_class="col"),
                    Div("userdefpri", css_class="col"),
                    css_class="form-row",
                ),
                Div(
                    Div("nobsblk", css_class="col"),
                    Div("instr_pri_0", css_class="col"),
                    Div("imgtype_0", css_class="col"),
                    css_class="form-row",
                ),
                # Added a button to choose sky transparency
                Div(
                    Div("maxseeing", css_class="col"),
                    Div("maxlunarphase", css_class="col"),
                    Div("minlunardist", css_class="col"),
                    Div("skytransparency", css_class="col"),
                    css_class="form-row",
                ),
                Div(
                    Div("timeconstraint", css_class="col"),
                    Div("timeref", css_class="col"),
                    Div("timewindow", css_class="col"),
                    css_class="form-row",
                ),
                Div(Div("mode_0", css_class="col"), css_class="form-row"),
            ),
            Fieldset(
                "Instrument Configuration",
                Div(
                    Div("dichroic_0", css_class="col"),
                    Div("red_grating_0", css_class="col"),
                    Div("blue_grating_0", css_class="col"),
                    css_class="form-row",
                ),
                Div(Div("aperturewheel_0", css_class="col"), css_class="form-row"),
            ),
            Fieldset(
                "Exposure",
                Div(
                    Div("exptime_0", css_class="col"),
                    Div("sky_exptime_0", css_class="col"),
                    Div("nexp_0", css_class="col"),
                    css_class="form-row",
                ),
                Div(
                    Div("scdescr_0", css_class="col"),
                    css_class="form-row",
                ),
                Div(Div("stellar_0", css_class="col"), css_class="form-row"),
                Div(
                    Div("binx_0", css_class="col"),
                    Div("biny_0", css_class="col"),
                    css_class="form-row",
                ),
            ),
            # Sky and nodding sequence
            Fieldset(
                "Sky Position",
                Div(Div("autoselsky_0", css_class="col"), css_class="form-row"),
                Div(
                    Div("skya_ra_0", css_class="col"),
                    Div("skya_dec_0", css_class="col"),
                    css_class="form-row",
                ),
            ),
            Fieldset(
                "Object Acquisition and guiding",
                Div(Div("autoselacqstar_0", css_class="col"), css_class="form-row"),
                Div(
                    Div("agfilter_0", css_class="col"),
                    Div("guide_0", css_class="col"),
                    css_class="form-row",
                ),
            ),
        )


# Class containing the business logic for interacting with the remote observatory.
# Includes methods to submit observations, check observation status, etc.
class ANU230cmFacility(BaseRoboticObservationFacility):
    name = "ANU 2.3m"

    observation_types = observation_forms = {"OBSERVATION": ANU230cmForm}

    SITES = {
        "ANU2.3m": {
            "latitude": -31.2716,
            "longitude": 149.062,
            "elevation": 1165,
        }
    }

    def get_form(self, observation_type):
        """
        This method takes in an observation type and returns the form type that matches it.
        """
        return ANU230cmForm

    def get_template_form(self, observation_type):
        """
        This method takes in an observation type and returns the form type that matches it.
        """
        return ANU230cmTemplateForm

    def cancel_observation(self, observation_id):
        """
        Takes an observation id and submits a request to the observatory that the observation be cancelled.

        If the cancellation was successful, return True. Otherwise, return False.
        """
        logger.info(f"Cancelling {observation_id}")

        url = settings.ANU_SITE + "removeobs.php"

        observation = ObservationRecord.objects.get(observation_id=observation_id)
        payload = observation.parameters
        proposal = payload.get("proposal")
        userdefid = payload.get("userdefid")

        get_data = {
            "PROPOSAL": proposal,
            "USERDEFID": userdefid,
            "Admin_Type": "JSON",
        }

        response = requests.get(
            url,
            params=get_data,
            auth=(settings.PROPOSAL_DB_USERNAME, settings.PROPOSAL_DB_PASSWORD),
        )

        try:
            logger.info(f"json response={response.content}")
        except Exception:
            msg = f"Bad response"
            logger.exception(msg)

        results = json.loads(response.content.decode())

        return results["status"]

    def get_observation_status(self, observation_id):
        """
        Return the status for a single observation. observation_id should
        be able to be used to retrieve the status from the external service.
        """
        # Add ANU2.3m POST request here.
        print(f"get_observation_status {observation_id}")
        # parting using the first hyphen
        tokens = observation_id.split("-", 1)

        # if less than 2 parts return to show error.
        if len(tokens) != 2:
            return {}

        # Keyword dictionary
        proposal_key = "PROPOSAL"
        offset_key = "OFFSET"
        pagesize_key = "PAGESIZE"
        filter_key = "FILTER"

        url = settings.ANU_SITE + "propobsstat.php"

        pagesize = 1000

        post_data = dict()
        post_data[proposal_key] = tokens[0]
        post_data[offset_key] = 0
        post_data[pagesize_key] = pagesize
        # this is to filter the result set by id
        post_data[filter_key] = tokens[1]

        try:
            observation = ObservationRecord.objects.get(observation_id=observation_id)
            state = observation.status
            scheduled_start = observation.scheduled_start
            scheduled_end = observation.scheduled_end
        except ObservationRecord.DoesNotExist:
            state = "Unknown"
            scheduled_start = None
            scheduled_end = None

        while True:
            response = requests.post(
                url,
                data=post_data,
                auth=(settings.PROPOSAL_DB_USERNAME, settings.PROPOSAL_DB_PASSWORD),
            )

            # FIXME: REPLACE WITH ACTUAL OBSERVATION TIMES.

            try:
                content = json.loads(response.content.decode())
                try:
                    data = content["data"]
                except KeyError:
                    # TODO: Decide whether observation should be deleted if not found...
                    # observation.delete()
                    return {
                        "state": content["msg"],
                        "scheduled_start": scheduled_start,
                        "scheduled_end": scheduled_end,
                    }
                logger.info(f"Number of observations found {len(data)}")
                # It is currently returning only one, need to check if there is a use case where it could return more
                for item in data:
                    logger.info(f"CHECK {item['userDefId']}  ==? {tokens[1]}")
                    if item["userDefId"] == tokens[1]:
                        state = item["obsStatus"]
                        logger.info(f"STATE={state}")

                        if state == "Succeeded":
                            return {
                                "state": state,
                                "scheduled_start": item["tsExec"],
                                "scheduled_end": item["tsExec"],
                            }

                if content["pageSize"] == pagesize:
                    post_data[offset_key] = post_data[offset_key] + pagesize
                else:
                    return {
                        "state": state,
                        "scheduled_start": scheduled_start,
                        "scheduled_end": scheduled_end,
                    }
            except Exception:
                msg = f"Bad response - I don't know how to show these in the tom message box."
                logger.exception(msg)
                return {
                    "state": state,
                    "scheduled_start": scheduled_start,
                    "scheduled_end": scheduled_end,
                }

    def get_observing_sites(self):
        """
        Return an iterable of dictionaries that contain the information
        necessary to be used in the planning (visibility) tool. The
        iterable should contain dictionaries each that contain sitecode,
        latitude, longitude and elevation. This is the static information
        about a site.
        """
        return self.SITES

    def get_terminal_observing_states(self):
        """
        Returns the states for which an observation is not expected
        to change.
        """
        return [
            "Succeeded",
            "Rejected",
            "No observations",
        ]  # Not sure if should be capitalised.

    @staticmethod
    def get_clean_data_for_posting(observation_payload):

        import astropy.units as u
        from astropy.coordinates import Angle

        # Keyword dictionary
        proposal = "PROPOSAL"
        userdefid = "USERDEFID"
        userdefpri = "USERDEFPRI"
        nobsblk = "NOBSBLK"

        maxseeing = "MAXSEEING"
        photometric = "PHOTOMETRIC"
        maxlunarphase = "MAXLUNARPHASE"
        minlunardist = "MINLUNARDIST"
        timeconstraint = "TIMECONSTRAINT"
        timeref = "TIMEREF"
        timewindow = "TIMEWINDOW"

        instr_pri_ = "INSTR_PRI_"
        imgtype_ = "IMGTYPE_"
        mode_ = "MODE_"
        ra_ = "RA_"
        dec_ = "DEC_"
        pmot_ = "PMOT_"
        rot_ = "ROT_"
        rotang_ = "ROTANG_"
        dichroic_ = "DICHROIC_"
        red_grating_ = "RED_GRATING_"
        blue_grating_ = "BLUE_GRATING_"
        aperturewheel_ = "APERTUREWHEEL_"
        agfilter_ = "AGFILTER_"
        stellar_ = "STELLAR_"
        binx_ = "BINX_"
        biny_ = "BINY_"
        nexp_ = "NEXP_"
        acq_ra_ = "ACQ_RA_"
        acq_dec_ = "ACQ_DEC_"
        acq_pmot_ = "ACQ_PMOT_"
        blindacq_ = "BLINDACQ_"
        guide_ = "GUIDE_"
        mag_ = "MAG_"
        exptime_ = "EXPTIME_"
        sky_exptime_ = "SKY_EXPTIME_"
        scdescr_ = "SCDESCR_"
        autoselsky_ = "AUTOSELSKY_"
        skya_ra_ = "SKYA_RA_"
        skya_dec_ = "SKYA_DEC_"

        post_data = {}
        post_data[proposal] = observation_payload["params"].get(proposal.lower(), None)
        post_data[userdefid] = observation_payload["params"].get(
            userdefid.lower(), None
        )
        post_data[userdefpri] = observation_payload["params"].get(
            userdefpri.lower(), None
        )
        post_data[nobsblk] = observation_payload["params"].get(nobsblk.lower(), None)
        post_data[maxseeing] = observation_payload["params"].get(
            maxseeing.lower(), None
        )
        post_data[photometric] = observation_payload["params"].get(
            photometric.lower(), None
        )
        post_data[maxlunarphase] = observation_payload["params"].get(
            maxlunarphase.lower(), None
        )
        post_data[minlunardist] = observation_payload["params"].get(
            minlunardist.lower(), None
        )
        post_data[timeconstraint] = observation_payload["params"].get(
            timeconstraint.lower(), None
        )
        post_data[timeref] = observation_payload["params"].get(timeref.lower(), None)
        post_data[timewindow] = observation_payload["params"].get(
            timewindow.lower(), None
        )
        post_data[instr_pri_ + "0"] = observation_payload["params"].get(
            instr_pri_.lower() + "0", None
        )
        post_data[imgtype_ + "0"] = observation_payload["params"].get(
            imgtype_.lower() + "0", None
        )
        post_data[mode_ + "0"] = observation_payload["params"].get(
            mode_.lower() + "0", None
        )
        post_data[dichroic_ + "0"] = observation_payload["params"].get(
            dichroic_.lower() + "0", None
        )
        post_data[red_grating_ + "0"] = observation_payload["params"].get(
            red_grating_.lower() + "0", None
        )  # ?
        post_data[blue_grating_ + "0"] = observation_payload["params"].get(
            blue_grating_.lower() + "0", None
        )
        post_data[aperturewheel_ + "0"] = observation_payload["params"].get(
            aperturewheel_.lower() + "0", None
        )
        post_data[ra_ + "0"] = observation_payload["params"].get(
            ra_.lower() + "0", None
        )
        post_data[dec_ + "0"] = observation_payload["params"].get(
            dec_.lower() + "0", None
        )
        post_data[pmot_ + "0"] = observation_payload["params"].get(
            pmot_.lower() + "0", None
        )
        # Add code to select acquisition star if requested
        post_data[acq_ra_ + "0"] = observation_payload["params"].get(
            acq_ra_.lower() + "0", None
        )
        post_data[acq_dec_ + "0"] = observation_payload["params"].get(
            acq_dec_.lower() + "0", None
        )
        post_data[acq_pmot_ + "0"] = observation_payload["params"].get(
            acq_pmot_.lower() + "0", None
        )
        post_data[blindacq_ + "0"] = observation_payload["params"].get(
            blindacq_.lower() + "0", None
        )
        post_data[rot_ + "0"] = observation_payload["params"].get(
            rot_.lower() + "0", None
        )
        post_data[rotang_ + "0"] = observation_payload["params"].get(
            rotang_.lower() + "0", None
        )
        post_data[mag_ + "0"] = observation_payload["params"].get(
            mag_.lower() + "0", None
        )
        post_data[agfilter_ + "0"] = observation_payload["params"].get(
            agfilter_.lower() + "0", None
        )
        post_data[guide_ + "0"] = observation_payload["params"].get(
            guide_.lower() + "0", None
        )
        post_data[nexp_ + "0"] = observation_payload["params"].get(
            nexp_.lower() + "0", None
        )
        post_data[stellar_ + "0"] = observation_payload["params"].get(
            stellar_.lower() + "0", None
        )
        post_data[binx_ + "0"] = observation_payload["params"].get(
            binx_.lower() + "0", None
        )
        post_data[biny_ + "0"] = observation_payload["params"].get(
            biny_.lower() + "0", None
        )
        post_data[exptime_ + "0"] = observation_payload["params"].get(
            exptime_.lower() + "0", None
        )
        post_data[sky_exptime_ + "0"] = observation_payload["params"].get(
            sky_exptime_.lower() + "0", None
        )
        post_data[scdescr_ + "0"] = observation_payload["params"].get(
            scdescr_.lower() + "0", None
        )

        # Code to select sky region if requested
        if observation_payload["params"].get(autoselsky_.lower() + "0"):
            obj_ra = observation_payload["params"].get(ra_.lower() + "0", None)
            obj_dec = observation_payload["params"].get(dec_.lower() + "0", None)

            obj_dict = {
                "RA": Angle(obj_ra, unit=u.hourangle).degree,
                "Dec": Angle(obj_dec, unit=u.degree).degree,
                "maskRadius": 20,
                "magLimit": 20,
                "Debug": False,
                "Verbose": False,
                "plotImage": False,
            }

            obj = SimpleNamespace(**obj_dict)

            sky = selectSky(obj)
            if sky["ra_sky"] is not None:
                observation_payload["params"][skya_ra_.lower() + "0"] = sky["ra_sky"]
                observation_payload["params"][skya_dec_.lower() + "0"] = sky["dec_sky"]
            else:
                # If a sky cannot be found,we set it 10' north of the object
                logger.info(
                    f"Cannot find sky. Setting a sky to 5' north of target. Good luck!"
                )
                observation_payload["params"][skya_ra_.lower() + "0"] = obj_dict["RA"]
                observation_payload["params"][skya_dec_.lower() + "0"] = (
                    obj_dict["Dec"] + 5 / 60
                )

        else:
            sky = {"ra_sky": None, "dec_sky": None}

        post_data[skya_ra_ + "0"] = observation_payload["params"].get(
            skya_ra_.lower() + "0", sky["ra_sky"]
        )
        post_data[skya_dec_ + "0"] = observation_payload["params"].get(
            skya_dec_.lower() + "0", sky["dec_sky"]
        )

        # Remove keys with None values
        post_data = {k: v for k, v in post_data.items() if v not in [None, ""]}

        return post_data, post_data[proposal], post_data[userdefid]

    def submit_observation(self, observation_payload):
        """
        This method takes in the serialized data from the form and actually
        submits the observation to the remote api
        """
        url = settings.ANU_SITE + "addobsblockexec.php"

        post_data, proposal, userdefid = self.get_clean_data_for_posting(
            observation_payload=observation_payload
        )

        response = requests.post(
            url,
            data=post_data,
            auth=(settings.PROPOSAL_DB_USERNAME, settings.PROPOSAL_DB_PASSWORD),
        )

        try:
            logger.info(f"json response={response.content}")
        except Exception:
            msg = f"Bad response"
            logger.exception(msg)

        return [f"{proposal}-{userdefid}"]

    def validate_observation(self, observation_payload):
        """
        Same thing as submit_observation, but a dry run. You can
        skip this in different modules by just using "pass"
        """
        pass

    def get_facility_weather_urls(self):
        """
        Returns a dictionary containing a URL for weather information
        for each site in the Facility SITES. This is intended to be useful
        in observation planning.

        `facility_weather = {'code': 'XYZ', 'sites': [ site_dict, ... ]}`
        where
        `site_dict = {'code': 'XYZ', 'weather_url': 'http://path/to/weather'}`

        """
        site_dict = {
            "code": "SSO",
            "weather_url": "https://www.mso.anu.edu.au/metdata/",
        }
        facility_weather = {"code": "SSO", "sites": [site_dict]}
        return facility_weather

    def get_facility_status(self):
        """
        Returns a dictionary describing the current availability of the Facility
        telescopes. This is intended to be useful in observation planning.
        The top-level (Facility) dictionary has a list of sites. Each site
        is represented by a site dictionary which has a list of telescopes.
        Each telescope has an identifier (code) and an status string.

        The dictionary hierarchy is of the form:

        `facility_dict = {'code': 'XYZ', 'sites': [ site_dict, ... ]}`
        where
        `site_dict = {'code': 'XYZ', 'telescopes': [ telescope_dict, ... ]}`
        where
        `telescope_dict = {'code': 'XYZ', 'status': 'AVAILABILITY'}`

        See lco.py for a concrete implementation example.
        """

        # Is there a way to query the telescope's status?

        telescope_dict = {"code": "ANU 2.3m", "status": "AVAILABLE"}
        site_dict = {"code": "SSO", "telescopes": [telescope_dict]}
        facility_dict = {"code": "SSO", "sites": [site_dict]}

        return facility_dict

    def get_observation_url(self, observation_id):
        url = settings.ARCHIVE_2M3_QUERY
        if url is None:
            return ""

        observation = ObservationRecord.objects.get(observation_id=observation_id)
        payload = observation.parameters
        proposal = payload.get("proposal")

        status = observation.status
        observationStart = observation.scheduled_start

        if observationStart is None:
            return ""

        if status != "Succeeded":
            return ""

        startDate = observationStart.strftime("%Y-%m-%d")
        endDate = observationStart + timedelta(days=1)
        endDate = endDate.strftime("%Y-%m-%d")

        postData = {
            "allocation_id": proposal,
            "start_date": startDate,
            "end_date": endDate,
        }

        try:
            response = requests.post(url, json=postData)
            content = json.loads(response.content.decode())[0]
        except Exception:
            msg = (
                f"Bad response - I don't know how to show these in the tom message box."
            )
            logger.exception(msg)
            return ""

        queryUrl = settings.ARCHIVE_2M3_RESULTS
        uuid = content.get("uuid")

        return f"{queryUrl}{uuid}"

    # Shouldn't need to use this. We won't host data.
    def data_products(self, observation_id, product_id=None):
        return []
