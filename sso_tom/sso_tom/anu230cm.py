from django import forms
from django.core.validators import RegexValidator

from crispy_forms.layout import Div, Layout, ButtonHolder, Submit, Fieldset
from crispy_forms.helper import FormHelper

from tom_observations.models import ObservationTemplate
from tom_observations.facility import BaseRoboticObservationFacility, BaseRoboticObservationForm
from tom_observations.observation_template import GenericTemplateForm

# Validators for form fields.
validate_ra = RegexValidator(
    regex=r"(?:[01][0-9]|[2][0-3])\s[0-5][0-9]\s[0-5][0-9][.][0-5][0-9]",
    message="RA must be specified with the format 'HH MM SS.SS'.",
    code="invalid",
    )

validate_dec = RegexValidator(
    regex=r"^[-+]?(?:[0-8][0-9]\s[0-5][0-9]\s[0-5][0-9][.][0-9]|90\s00\s00[.]0)$",
    message="Declination must be specified with the format 'sDD MM SS.S'.",
    code="invalid",
    )

# Class that displays a GUI form for users to create an observation.
class ANU230cmForm(BaseRoboticObservationForm):

    TIMECONSTRAINT_CHOICES = [
        ("Flexible", "Flexible"),
        ("Fixed", "Fixed"),
    ]

    MODE_CHOICES = [
        ("ClassicalEqual", "Classical Equal"),
        ("ObjectSkyNodAndShuffle", "Object Sky Nod And Shuffle"),
    ]

    DICHROIC_CHOICES = [
        ("RT480", "RT480"),
        ("RT560", "RT560"),
        ("RT615", "RT615"),
    ]

    RED_GRATING_CHOICES = [
        ("R3000", "R3000"),
        ("R7000", "R7000"),
        ("I7000", "I7000"),
    ]

    BLUE_GRATING_CHOICES = [
        ("B3000", "B3000"),
        ("B7000", "B7000"),
        ("U7000", "U7000"),
    ]

    ROT_CHOICES = [
        ("PA", "Position Angle"),
        ("VA", "Vert. Angle (init)"),
    ]

    AGFILTER_CHOICES = [
        ("No Change", "None"),
        ("B", "B"),
        ("V", "V"),
        ("R", "R"),
        ("I", "I"),
        ("ND", "ND"),
    ]

    GUIDE_CHOICES = [
        ("No", "No"),
        ("BestEffort", "Best Effort"),
        ("AcqStar", "Acquire Star"),
    ]

    STELLAR_CHOICES = [
        ("True", "Stellar"),
        ("False", "Full Field"),
    ]
    BINX_CHOICES = [
        (1, "1"),
        (2, "2"),
    ]

    BINY_CHOICES = [
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
    ]

    proposal = forms.CharField(label="Proposal ID",)
    userdefid = forms.CharField(label="User Def. ID",)
    userdefpri = forms.IntegerField(label="User Def. Priority", initial=0,)
    nobsblk = forms.IntegerField(label="No. Obs. Blocks", initial=1, disabled=True,)
    maxseeing = forms.CharField(label='Max Seeing (")', required=False,)
    photometric = forms.BooleanField(label="Photometric", required=False,)
    maxlunarphase = forms.IntegerField(label="Max. Lunar Phase (%)", required=False, initial=100,)
    timeconstraint = forms.ChoiceField(label="Time Constraint", required=False, choices=TIMECONSTRAINT_CHOICES, initial="Flexible",)
    # timeref = forms.DateTimeField(label="Time Ref. (UTC)", required=False,)
    timeref = forms.CharField(label="Time Ref. (UTC)",
                              required=False,
                              widget=forms.DateTimeInput(attrs={'type': 'datetime'}, format='%Y-%m-%d %H:%M:%S'),)
    timewindow = forms.IntegerField(label="Time Window", required=False,)
    instr_pri_0 = forms.CharField(label="Primary Instrument", required=False, initial="WiFeS", disabled=True,)
    imgtype_0 = forms.CharField(label="Image Type", required=False, initial="Object", disabled=True,)
    mode_0 = forms.ChoiceField(label="Mode", choices=MODE_CHOICES, initial="ClassicalEqual",)
    dichroic_0 = forms.ChoiceField(label="Dichroic", choices=DICHROIC_CHOICES,)
    red_grating_0 = forms.ChoiceField(label="Red Grating", choices=RED_GRATING_CHOICES,)
    blue_grating_0 = forms.ChoiceField(label="Blue Grating", choices=BLUE_GRATING_CHOICES,)
    aperturewheel_0 = forms.CharField(label="Aperture Wheel", required=False, initial="Clear",)
    ra_0 = forms.CharField(label="RA", validators=[validate_ra],)
    dec_0 = forms.CharField(label="Dec", validators=[validate_dec],)
    pmot_0 = forms.CharField(label="Prop. Motion", required=False,)
    acq_ra_0 = forms.CharField(label="Acquired RA", required=False,)
    acq_dec_0 = forms.CharField(label="Acquired Dec", required=False,)
    acq_pmot_0 = forms.CharField(label="Acq. Prop. Motion", required=False,)
    blindacq_0 = forms.BooleanField(label="Blind Acquisition", required=False, initial=False,)
    rot_0 = forms.ChoiceField(label="Rotation", choices=ROT_CHOICES, initial="PA",)
    rotang_0 = forms.FloatField(label="Rotation Angle", required=False, initial=0.0,)
    mag_0 = forms.FloatField(label="Magnitude", required=False,)
    agfilter_0 = forms.ChoiceField(label="A&G Filter", required=False, choices=AGFILTER_CHOICES, initial="No Change",)
    guide_0 = forms.ChoiceField(label="Guiding", required=False, choices=GUIDE_CHOICES, initial="BestEffort",)
    nexp_0 = forms.IntegerField(label="Num. Exposures", required=False, initial=1,)
    stellar_0 = forms.ChoiceField(label="Region of Interest", required=False, choices=STELLAR_CHOICES, initial="False",)
    binx_0 = forms.ChoiceField(label="Spectral Binning", required=False, choices=BINX_CHOICES, initial=1,)
    biny_0 = forms.ChoiceField(label="Spatial Binning", required=False, choices=BINY_CHOICES, initial=2,)
    exptime_0 = forms.IntegerField(label="Exposure time (s)", initial=150,)
    sky_exptime_0 = forms.IntegerField(label="Sky Exp. time (s)", required=False,)
    scdescr_0 = forms.CharField(label="Sub-cycle Description", required=False,)
    skya_ra_0 = forms.CharField(label="Sky A RA", required=False,)
    skya_dec_0 = forms.CharField(label="Sky A Dec", required=False,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_id = "6"
        self.helper.layout = Layout(
            self.common_layout,
            self.layout(),
            self.button_layout(),
        )

    def layout(self):
        return Div(
            Fieldset(
                'Observation',
                Div(
                    Div('proposal', css_class='col'),
                    Div('userdefid', css_class='col'),
                    Div('userdefpri', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('nobsblk', css_class='col'),
                    Div('instr_pri_0', css_class='col'),
                    Div('imgtype_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('maxseeing', css_class='col'),
                    Div('maxlunarphase', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('timeconstraint', css_class='col'),
                    Div('timeref', css_class='col'),
                    Div('timewindow', css_class='col'),
                    css_class='form-row'
                ),
                Div('mode_0', css_class='form-row'),
            ),
            Fieldset(
                'Instrument Configuration',
                Div(
                    Div('dichroic_0', css_class='col'),
                    Div('red_grating_0', css_class='col'),
                    Div('blue_grating_0', css_class='col'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Exposure',
                Div(
                    Div('exptime_0', css_class='col'),
                    Div('sky_exptime_0', css_class='col'),
                    Div('nexp_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('stellar_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('binx_0', css_class='col'),
                    Div('biny_0', css_class='col'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Object, Acquisition & Guide',
                Div(
                    Div('ra_0', css_class='col'),
                    Div('dec_0', css_class='col'),
                    Div('pmot_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('acq_ra_0', css_class='col'),
                    Div('acq_dec_0', css_class='col'),
                    Div('acq_pmot_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('blindacq_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('rot_0', css_class='col'),
                    Div('rotang_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('mag_0', css_class='col'),
                    Div('agfilter_0', css_class='col'),
                    Div('guide_0', css_class='col'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Nod & Shuffle Sky',
                Div(
                    Div('scdescr_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('skya_ra_0', css_class='col'),
                    Div('skya_dec_0', css_class='col'),
                    css_class='form-row'
                ),
            ),
        )

    def button_layout(self):
        # target_id = self.initial.get('target_id')
        return ButtonHolder(
                Submit('submit', 'Submit'),
                # HTML(f'''<a class="btn btn-outline-primary" href={{% url 'tom_targets:detail' {target_id} %}}>
                #          Back</a>''')
            )


# Class that displays a GUI form for users to create an observation template.
class ANU230cmTemplateForm(GenericTemplateForm):

    TIMECONSTRAINT_CHOICES = [
        ("Flexible", "Flexible"),
        ("Fixed", "Fixed"),
    ]

    MODE_CHOICES = [
        ("ClassicalEqual", "Classical Equal"),
        ("ObjectSkyNodAndShuffle", "Object Sky Nod And Shuffle"),
    ]

    DICHROIC_CHOICES = [
        ("RT480", "RT480"),
        ("RT560", "RT560"),
        ("RT615", "RT615"),
    ]

    RED_GRATING_CHOICES = [
        ("R3000", "R3000"),
        ("R7000", "R7000"),
        ("I7000", "I7000"),
    ]

    BLUE_GRATING_CHOICES = [
        ("B3000", "B3000"),
        ("B7000", "B7000"),
        ("U7000", "U7000"),
    ]

    ROT_CHOICES = [
        ("PA", "Position Angle"),
        ("VA", "Vert. Angle (init)"),
    ]

    AGFILTER_CHOICES = [
        ("No Change", "None"),
        ("B", "B"),
        ("V", "V"),
        ("R", "R"),
        ("I", "I"),
        ("ND", "ND"),
    ]

    GUIDE_CHOICES = [
        ("No", "No"),
        ("BestEffort", "Best Effort"),
        ("AcqStar", "Acquire Star"),
    ]

    STELLAR_CHOICES = [
        ("True", "Stellar"),
        ("False", "Full Field"),
    ]
    BINX_CHOICES = [
        (1, "1"),
        (2, "2"),
    ]

    BINY_CHOICES = [
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
    ]

    proposal = forms.CharField(label="Proposal ID", required=False,)
    userdefid = forms.CharField(label="User Def. ID", required=False,)
    userdefpri = forms.IntegerField(label="User Def. Priority", initial=0, required=False,)
    nobsblk = forms.IntegerField(label="No. Obs. Blocks", initial=1, disabled=True,)
    maxseeing = forms.CharField(label='Max Seeing (")', required=False,)
    photometric = forms.BooleanField(label="Photometric", required=False,)
    maxlunarphase = forms.IntegerField(label="Max. Lunar Phase (%)", required=False, initial=100,)
    timeconstraint = forms.ChoiceField(label="Time Constraint", required=False, choices=TIMECONSTRAINT_CHOICES, initial="Flexible",)
    timeref = forms.DateTimeField(label="Time Ref. (UTC)", required=False,)
    timewindow = forms.IntegerField(label="Time Window", required=False,)
    instr_pri_0 = forms.CharField(label="Primary Instrument", required=False, initial="WiFeS", disabled=True,)
    imgtype_0 = forms.CharField(label="Image Type", required=False, initial="Object", disabled=True,)
    mode_0 = forms.ChoiceField(label="Mode", choices=MODE_CHOICES, initial="ClassicalEqual",)
    dichroic_0 = forms.ChoiceField(label="Dichroic", choices=DICHROIC_CHOICES,)
    red_grating_0 = forms.ChoiceField(label="Red Grating", choices=RED_GRATING_CHOICES,)
    blue_grating_0 = forms.ChoiceField(label="Blue Grating", choices=BLUE_GRATING_CHOICES,)
    aperturewheel_0 = forms.CharField(label="Aperture Wheel", required=False, initial="Clear",)
    # ra_0 = forms.CharField(label="RA", validators=[validate_ra],)
    # dec_0 = forms.CharField(label="Dec", validators=[validate_dec],)
    ra_0 = forms.CharField(label="RA", validators=[validate_ra], required=False, disabled=True,)
    dec_0 = forms.CharField(label="Dec", validators=[validate_dec], required=False, disabled=True,)
    pmot_0 = forms.CharField(label="Prop. Motion", required=False,)
    acq_ra_0 = forms.CharField(label="Acquired RA", required=False,)
    acq_dec_0 = forms.CharField(label="Acquired Dec", required=False,)
    acq_pmot_0 = forms.CharField(label="Acq. Prop. Motion", required=False,)
    blindacq_0 = forms.BooleanField(label="Blind Acquisition", required=False, initial=False,)
    rot_0 = forms.ChoiceField(label="Rotation", choices=ROT_CHOICES, initial="PA",)
    rotang_0 = forms.FloatField(label="Rotation Angle", required=False, initial=0.0,)
    mag_0 = forms.FloatField(label="Magnitude", required=False,)
    agfilter_0 = forms.ChoiceField(label="A&G Filter", required=False, choices=AGFILTER_CHOICES, initial="No Change",)
    guide_0 = forms.ChoiceField(label="Guiding", required=False, choices=GUIDE_CHOICES, initial="BestEffort",)
    nexp_0 = forms.IntegerField(label="Num. Exposures", required=False, initial=1,)
    stellar_0 = forms.ChoiceField(label="Region of Interest", required=False, choices=STELLAR_CHOICES, initial="False",)
    binx_0 = forms.ChoiceField(label="Spectral Binning", required=False, choices=BINX_CHOICES, initial=1,)
    biny_0 = forms.ChoiceField(label="Spatial Binning", required=False, choices=BINY_CHOICES, initial=2,)
    exptime_0 = forms.IntegerField(label="Exposure time (s)", initial=150, required=False,)
    sky_exptime_0 = forms.IntegerField(label="Sky Exp. time (s)", required=False,)
    scdescr_0 = forms.CharField(label="Sub-cycle Description", required=False,)
    skya_ra_0 = forms.CharField(label="Sky A RA", required=False,)
    skya_dec_0 = forms.CharField(label="Sky A Dec", required=False,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.common_layout = Layout('facility', 'template_name')
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            self.common_layout,
            self.layout(),
        )
    
    def layout(self):
        return Div(
            Fieldset(
                'Observation',
                Div(
                    Div('proposal', css_class='col'),
                    Div('userdefid', css_class='col'),
                    Div('userdefpri', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('nobsblk', css_class='col'),
                    Div('instr_pri_0', css_class='col'),
                    Div('imgtype_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('maxseeing', css_class='col'),
                    Div('maxlunarphase', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('timeconstraint', css_class='col'),
                    Div('timeref', css_class='col'),
                    Div('timewindow', css_class='col'),
                    css_class='form-row'
                ),
                Div('mode_0', css_class='form-row'),
            ),
            Fieldset(
                'Instrument Configuration',
                Div(
                    Div('dichroic_0', css_class='col'),
                    Div('red_grating_0', css_class='col'),
                    Div('blue_grating_0', css_class='col'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Exposure',
                Div(
                    Div('exptime_0', css_class='col'),
                    Div('sky_exptime_0', css_class='col'),
                    Div('nexp_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('stellar_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('binx_0', css_class='col'),
                    Div('biny_0', css_class='col'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Object, Acquisition & Guide',
                Div(
                    Div('ra_0', css_class='col'),
                    Div('dec_0', css_class='col'),
                    Div('pmot_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('acq_ra_0', css_class='col'),
                    Div('acq_dec_0', css_class='col'),
                    Div('acq_pmot_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('blindacq_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('rot_0', css_class='col'),
                    Div('rotang_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('mag_0', css_class='col'),
                    Div('agfilter_0', css_class='col'),
                    Div('guide_0', css_class='col'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Nod & Shuffle Sky',
                Div(
                    Div('scdescr_0', css_class='col'),
                    css_class='form-row'
                ),
                Div(
                    Div('skya_ra_0', css_class='col'),
                    Div('skya_dec_0', css_class='col'),
                    css_class='form-row'
                ),
            ),
        )


# Class containing the business logic for interacting with the remote observatory.
# Includes methods to submit observations, check observation status, etc.
class ANU230cmFacility(BaseRoboticObservationFacility):

    name = 'ANU 2.3m'

    observation_types = observation_forms = {
       'OBSERVATION': ANU230cmForm 
    }

    SITES = {
        'ANU2.3m': {
            'latitude': -31.2716,
            'longitude': 149.062,
            'elevation': 1165,
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

    def get_observation_status(self, observation_id):
        """
        Return the status for a single observation. observation_id should
        be able to be used to retrieve the status from the external service.
        """
        # Add ANU2.3m API query here.
        return ['Pending']

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
        return ['Succeeded', 'Rejected'] # Not sure if should be capitalised.

    def submit_observation(self, observation_payload):
        """
        This method takes in the serialized data from the form and actually
        submits the observation to the remote api
        """
        # Add ANU2.3m API query here.
        print(observation_payload)
        return [1]

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
        site_dict = {'code': 'SSO', 'weather_url': 'https://www.mso.anu.edu.au/metdata/'}
        facility_weather = {'code': 'SSO', 'sites': [site_dict]}
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

        telescope_dict = {'code': 'ANU 2.3m', 'status': 'AVAILABLE'}
        site_dict = {'code': 'SSO', 'telescopes': [telescope_dict]}
        facility_dict = {'code': 'SSO', 'sites': [site_dict]}

        return facility_dict
    
    def get_observation_url(self, observation_id):
        return ''

    # Shouldn't need to use this. We won't host data.
    def data_products(self, observation_id, product_id=None):
        return []