import uuid

from django import forms
from django.core.validators import RegexValidator

import requests
import json
import logging
from datetime import timedelta
from django.utils import timezone

from crispy_forms.layout import Div, Layout, ButtonHolder, Submit, Fieldset
from crispy_forms.helper import FormHelper

from tom_observations.models import ObservationTemplate
from tom_observations.facility import (
    BaseRoboticObservationFacility,
    BaseRoboticObservationForm,
)
from tom_observations.observation_template import GenericTemplateForm
from tom_targets.models import Target
from decouple import config

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
        ("RT480", "RT480"),
        ("RT560", "RT560"),
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
        ("No Change", "None"),
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

# Validators for form fields.
# validate_ra = RegexValidator(
#     regex=r"(?:[01][0-9]|[2][0-3])\s[0-5][0-9]\s[0-5][0-9][.][0-5][0-9]",
#     message="RA must be specified with the format 'HH MM SS.SS'.",
#     code="invalid",
# )

# validate_dec = RegexValidator(
#     regex=r"^[-+]?(?:[0-8][0-9]\s[0-5][0-9]\s[0-5][0-9][.][0-9]|90\s00\s00[.]0)$",
#     message="Declination must be specified with the format 'sDD MM SS.S'.",
#     code="invalid",
# )

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
    photometric = forms.BooleanField(
        label="Photometric",
        required=False,
    )
    maxlunarphase = forms.IntegerField(
        label="Max. Lunar Phase (%)",
        required=False,
        initial=100,
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
        # validators=[validate_ra],
        required=False,
        disabled=True,
    )
    dec_0 = forms.CharField(
        label="Dec",
        # validators=[validate_dec],
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
        initial="No Change",
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
    skya_ra_0 = forms.CharField(
        label="Sky A RA",
        required=False,
    )
    skya_dec_0 = forms.CharField(
        label="Sky A Dec",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            self.common_layout,
            self.layout(),
            self.button_layout(),
        )

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
                    Div("maxlunarphase", css_class="col"),
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
            Fieldset(
                "Nod & Shuffle Sky",
                Div(Div("scdescr_0", css_class="col"), css_class="form-row"),
                Div(
                    Div("skya_ra_0", css_class="col"),
                    Div("skya_dec_0", css_class="col"),
                    css_class="form-row",
                ),
            ),
        )

    def button_layout(self):
        # target_id = self.initial.get('target_id')
        return ButtonHolder(
            Submit("submit", "Submit"),
            # HTML(f'''<a class="btn btn-outline-primary" href={{% url 'tom_targets:detail' {target_id} %}}>
            #          Back</a>''')
        )

    def observation_payload(self):
        """
        This method is called to extract the data from the form into a dictionary that
        can be used by the rest of the module. In the base implementation it simply dumps
        the form into a json string.
        """
        from astropy.coordinates import Angle
        from astropy import units

        target = Target.objects.get(pk=self.cleaned_data['target_id'])

        # Convert ra/dec Target fields back to strings of correct format
        # and add them to Observation data.
        self.cleaned_data['ra_0'] = Angle(target.ra, unit=units.degree).to_string(unit=units.hourangle, sep=' ')
        self.cleaned_data['dec_0'] = Angle(target.dec, unit=units.degree).to_string(unit=units.degree, sep=' ')

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
        self.cleaned_data['pmot_0'] = f'{pmot_ra} {pmot_dec}'

        return {
            'target_id': target.id,
            'params': self.serialize_parameters()
        }

# Class that displays a GUI form for users to create an observation template.
class ANU230cmTemplateForm(GenericTemplateForm):

    proposal = forms.CharField(
        label="Proposal ID",
        required=False,
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
    photometric = forms.BooleanField(
        label="Photometric",
        required=False,
    )
    maxlunarphase = forms.IntegerField(
        label="Max. Lunar Phase (%)",
        required=False,
        initial=100,
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
        # validators=[validate_ra],
        required=False,
        disabled=True,
    )
    dec_0 = forms.CharField(
        label="Dec",
        # validators=[validate_dec],
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
        initial="No Change",
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
        super().__init__(*args, **kwargs)
        self.common_layout = Layout("facility", "template_name")
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))
        self.helper.layout = Layout(
            self.common_layout,
            self.layout(),
        )

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
                    Div("maxlunarphase", css_class="col"),
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
            Fieldset(
                "Nod & Shuffle Sky",
                Div(Div("scdescr_0", css_class="col"), css_class="form-row"),
                Div(
                    Div("skya_ra_0", css_class="col"),
                    Div("skya_dec_0", css_class="col"),
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
        print(f"Cancelling {observation_id}")
        return True

    def get_observation_status(self, observation_id):
        """
        Return the status for a single observation. observation_id should
        be able to be used to retrieve the status from the external service.
        """
        # Add ANU2.3m POST request here.
        test_anu230cm_emulator = True
        if test_anu230cm_emulator:
            print(f"get_observation_status {observation_id}")
            tokens = observation_id.split("-")
            print(f"get_observation_status user email = {dir(self)}")
            print(f"get_observation_status user email = {self.user}")
            # local version of emuldate_common
            ADACS_PROPOSALDB_TEST_PASSWORD = config('ADACS_PROPOSALDB_TEST_PASSWORD')
            ADACS_PROPOSALDB_TEST_USERNAME = config('ADACS_PROPOSALDB_TEST_USERNAME')
            emulate_ANU230cm="https://mortal.anu.edu.au/aocs/"
            print(f"TOKENS FOR ACCESS {ADACS_PROPOSALDB_TEST_PASSWORD} {ADACS_PROPOSALDB_TEST_USERNAME}")
            #url_suffix = "/"
            url_suffix = ".php"
            # Keyword dictionary
            PROPOSAL="PROPOSAL"
            USERDEFID="USERDEFID"
            USERDEFPRI="USERDEFPRI"
            NOBSBLK="NOBSBLK"

            url = emulate_ANU230cm+'/propobsstat'+url_suffix

            post_data = {}
            post_data[PROPOSAL]=tokens[0]
            post_data["OFFSET"]=0
            post_data["PAGESIZE"]=1000
            print(f"get_observation_status {observation_id}")
            response = requests.post(url, data=post_data, auth=(ADACS_PROPOSALDB_TEST_USERNAME, ADACS_PROPOSALDB_TEST_PASSWORD))
            try:
                content = json.loads(response.content.decode())
                print(f"!content={content}")
                found = False
                data = content["data"]
                print(f"Number of observations in this proposal {len(data)}")
                state = "PENDING"
                for i in range(len(data)):
                    print(f"CHECK {data[i]['userDefId']}  ==? {tokens[1]}")
                    if data[i]["userDefId"] == tokens[1]:
                        found = True
                        state = data[i]['obsStatus']
                print(f"STATE={state}")
            except Exception:
                msg = f"Bad response - I don't know how to show these in the tom message box."
                logger.exception(msg)

            if not found:
                return {}

            #return content["data"]
            return {
                'state': state,
                'scheduled_start': timezone.now() + timedelta(hours=1),
                'scheduled_end': timezone.now() + timedelta(hours=2)
            }

        # ${SERVER}/aocs/propobsstat.php?PROPOSAL=<number>&OFFSET=<integer>&PAGESIZE=<integer>&FILTER=<string>
        # - OFFSET and PAGESIZE: for requesting multiple observations status updates.
        # - FILTER: pattern-matching for userdefid (query specific requests).
        # - Status received in “data” array. Each entry a dict w. userDefId, obsStatus, tsExec, …
        # - tsExec is UTC timestamp of last status change: YYYY-MM-DDThh:mm:ss or ‘’

        return ['PENDING']

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
        return ["Succeeded", "Rejected"]  # Not sure if should be capitalised.

    def submit_observation(self, observation_payload):
        """
        This method takes in the serialized data from the form and actually
        submits the observation to the remote api
        """
        # Add ANU2.3m API query here.
        test_anu230cm_emulator = True
        if test_anu230cm_emulator:
            print("new submit_observation_payload")
            # local version of emuldate_common
            ADACS_PROPOSALDB_TEST_PASSWORD = 'asdffdsafdsadfs' # config('ADACS_PROPOSALDB_TEST_PASSWORD')
            ADACS_PROPOSALDB_TEST_USERNAME = 'uiooiuiiooiu' #config('ADACS_PROPOSALDB_TEST_USERNAME')
            emulate_ANU230cm="https://mortal.anu.edu.au/aocs/"
            print(f"TOKENS FOR ACCESS {ADACS_PROPOSALDB_TEST_PASSWORD} {ADACS_PROPOSALDB_TEST_USERNAME}")
            #url_suffix = "/"
            url_suffix = ".php"
            # Keyword dictionary
            PROPOSAL="PROPOSAL"
            USERDEFID="USERDEFID"
            USERDEFPRI="USERDEFPRI"
            NOBSBLK="NOBSBLK"

            MAXSEEING="MAXSEEING"
            PHOTOMETRIC="PHOTOMETRIC"
            MAXLUNARPHASE="MAXLUNARPHASE"
            TIMECONSTRAINT="TIMECONSTRAINT"
            TIMEREF="TIMEREF"
            TIMEWINDOW="TIMEWINDOW"

            INSTR_PRI_ = "INSTR_PRI_"
            IMGTYPE_ = "IMGTYPE_"
            MODE_ = "MODE_"
            RA_ = "RA_"
            DEC_ = "DEC_"
            PMOT_ = "PMOT_"
            ROT_ = "ROT_"
            ROTANG_ = "ROTANG_"
            DICHROIC_ = "DICHROIC_"
            RED_GRATING_ = "RED_GRATING_"
            BLUE_GRATING_ = "BLUE_GRADING_"
            APERTUREWHEEL_ = "APERTUREWHEEL_"
            AGFILTER_ = "AGFILTER_"
            STELLAR_ = "STELLAR_"
            BINX_ = "BINX_"
            BINY_ = "BINY_"
            NEXP_ = "NEXP_"
            ACQ_RA_ = "ACQ_RA_"
            ACQ_DEC_ = "ACQ_DEC_"
            ACQ_PMOT_ = "ACQ_PMOT_"
            BLINDACQ_ = "BLINDACQ_"
            GUIDE_ = "GUIDE_"
            MAG_ = "MAG_"
            EXPTIME_ = "EXPTIME_"
            SKY_EXPTIME_ = "SKY_EXPTIME_"
            SCDESCR_ = "SCDESCR_"
            SKYA_RA_ = "SKYA_RA_"
            SKYA_DEC_ = "SKYA_DEC_"

            #
            url = emulate_ANU230cm+'/addobsblockexec'+url_suffix

            post_data = {}
            post_data[PROPOSAL]=observation_payload['params']['proposal']

            print(observation_payload)

            # crosscheck list of whats on the observation_payload
            # cadence_strategy: ignored
            # facility: 'ANU 2.3m'
            # target_id: ignored
            # observation_type: ignored
            # proposal: passed
            # userdefid: passed as USERDEFID
            # nobsblk: 1 passed as NOBSBLK
            # maxseeing: passed as MAXSEEING
            # photometric: passed as PHOTOMETRIC
            # maxlunarphase: passed as MAXLUNARPHASE
            # timeconstraint: passed as TIMECONSTRAINT
            # timeref: passed as TIMEREF
            # timewindow: passed as TIMEWINDOW
            # instr_pri_0: passed as INSTR_PRI_0
            # imgtype_0: passed as INSTR_PRI_0
            # mode_0: passed as MODE_0
            # dichroic_0: passed as DICHROIC_0
            # red_grating_0: passed as RED_GRATING_0
            # blue_grating_0: passed as BLUE_GRATING_0
            # aperturewheel_0: passed as APERTUREWHEEL_0
            # ra_0: passed as RA_0
            # dec_0: passed as DEC_0
            # pmot_0: passed as PMOT
            # acq_ra_0: passed as ACQ_RA_0
            # acq_dec_0: passed as ACQ_DEC_0
            # acq_pmot_0: passed as ACQ_PMOT_0
            # blindacq_0: passed BLINDACQ_0
            # rot_0: passed as ROT_0
            # rotang_0: passed as ROTANG_0
            # mag_0: passed as MAG_0
            # agfilter_0: passed AGFILTER_0
            # guide_0: passed as GUIDE_0
            # nexp_0: passed as NEXP_0
            # stellar_0: passed as STELLAR_0
            # binx_0: passed as BINX_0
            # biny_0: passed as BINY_0
            # exptime_0: passed as EXPTIME_0
            # sky_exptime_0: passed as SKY_EXPTIME_0
            # scdescr_0: passed as SCDESCR_0
            # skya_ra_0: passed as SKYA_RA_0
            # skya_dec_0: passed as SKYA_DEC_0

            post_data[USERDEFID]=observation_payload['params']['userdefid']
            post_data[USERDEFPRI]=observation_payload['params']['userdefpri']
            post_data[NOBSBLK] = 1
            post_data[MAXSEEING]=observation_payload['params']['maxseeing']
            post_data[PHOTOMETRIC]=observation_payload['params']['photometric']
            post_data[MAXLUNARPHASE]=observation_payload['params']['maxlunarphase']
            post_data[TIMECONSTRAINT]=observation_payload['params']['timeconstraint']
            post_data[TIMEREF]=observation_payload['params']['timeref']
            post_data[TIMEWINDOW]=observation_payload['params']['timewindow']
            post_data[INSTR_PRI_+"0"]=observation_payload['params']['instr_pri_0']
            post_data[IMGTYPE_+"0"]=observation_payload['params']['imgtype_0']
            post_data[MODE_+"0"]=observation_payload['params']['mode_0']
            post_data[DICHROIC_+"0"]=observation_payload['params']['dichroic_0']
            post_data[RED_GRATING_+"0"]=observation_payload['params']['red_grating_0']  #?
            post_data[BLUE_GRATING_+"0"]=observation_payload['params']['blue_grating_0']
            post_data[APERTUREWHEEL_+"0"]=observation_payload['params']['aperturewheel_0']
            post_data[RA_+"0"]=observation_payload['params']['ra_0']
            post_data[DEC_+"0"]=observation_payload['params']['dec_0']
            post_data[PMOT_+"0"]=observation_payload['params']['pmot_0']
            post_data[ACQ_RA_+"0"]=observation_payload['params']['acq_ra_0']
            post_data[ACQ_DEC_+"0"]=observation_payload['params']['acq_dec_0']
            post_data[ACQ_PMOT_+"0"]=observation_payload['params']['acq_pmot_0']
            post_data[BLINDACQ_+"0"]=observation_payload['params']['blindacq_0']
            post_data[ROT_+"0"]=observation_payload['params']['rot_0']
            post_data[ROTANG_+"0"]=observation_payload['params']['rotang_0']
            post_data[MAG_+"0"]=observation_payload['params']['mag_0']
            post_data[AGFILTER_+"0"]=observation_payload['params']['agfilter_0']
            post_data[GUIDE_+"0"]=observation_payload['params']['guide_0']
            post_data[NEXP_+"0"]=observation_payload['params']['nexp_0']
            post_data[STELLAR_+"0"]=observation_payload['params']['stellar_0']
            post_data[BINX_+"0"]=observation_payload['params']['binx_0']
            post_data[BINY_+"0"]=observation_payload['params']['biny_0']
            post_data[EXPTIME_+"0"]=observation_payload['params']['exptime_0']
            post_data[SKY_EXPTIME_+"0"]=observation_payload['params']['sky_exptime_0']
            post_data[SCDESCR_+"0"]=observation_payload['params']['scdescr_0']
            post_data[SKYA_RA_+"0"]=observation_payload['params']['skya_ra_0']
            post_data[SKYA_DEC_+"0"]=observation_payload['params']['skya_dec_0']
            #
            response = requests.post(url, data=post_data, auth=(ADACS_PROPOSALDB_TEST_USERNAME, ADACS_PROPOSALDB_TEST_PASSWORD))
            print(f"{response}")

            try:
                #content = json.loads(response.content)
                print(f"json response={response.content}")
            except Exception:
                msg = f"Bad response"
                logger.exception(msg)

            return [post_data[PROPOSAL]+"-"+post_data[USERDEFID]]
        return [uuid.uuid4()]  # update it to unique

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
        return ""

    # Shouldn't need to use this. We won't host data.
    def data_products(self, observation_id, product_id=None):
        return []
