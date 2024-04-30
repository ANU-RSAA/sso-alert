# Copyright (c) 2024 Jamie Soon
#
# This file is part of TOM Toolkit/SSO-Alert.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


"""
Basically there are very limited amount of methods to send/receive information.
Therefore, most systems will likely use REST methods.

Also, in reality, requesting observations is the same commands over and over.
Therefore can probably generalise such that a user only needs to create a settings
file and load from there instead of rewriting an entire module.

This is a copy of ocs.py but generalised a bit more.
"""

import logging
import requests

from crispy_forms.layout import Div, HTML, Layout, ButtonHolder, Submit
from django import forms
from django.conf import settings

from tom_common.exceptions import ImproperCredentialsException
from tom_observations.facility import (
    BaseRoboticObservationFacility,
    BaseRoboticObservationForm,
)
from tom_observations.observation_template import GenericTemplateForm
from tom_targets.models import (
    Target,
)

logger = logging.getLogger(__name__)


class RESTSettings:
    """Class encapsulates the settings from django for this Facility, and some of the options for
    an REST form implementation. The facility_name is used for retrieving the settings from the
    FACILITIES dictionary in settings.py.
    """

    def __init__(self, facility_name: str) -> None:
        self.facility_name = facility_name

    def get_setting(self, key: str) -> bool | dict | list | str | None:
        return settings.FACILITIES.get(self.facility_name).get(key)

    def get_observing_states(self) -> list:
        return (
            self.get_pending_observing_states()
            + self.get_successful_observing_states()
            + self.get_failed_observing_states()
        )

    def get_pending_observing_states(self) -> list:
        return self.get_setting("observing_states").get("pending")

    def get_successful_observing_states(self) -> list:
        return self.get_setting("observing_states").get("successful")

    def get_failed_observing_states(self) -> list:
        return self.get_setting("observing_states").get("failed")

    def get_terminal_observing_states(self) -> list:
        return (
            self.get_successful_observing_states() + self.get_failed_observing_states()
        )

    def get_fits_facility_header_keyword(self) -> str:
        return self.get_setting("data").get("fits_facility_header_keyword")

    def get_fits_facility_header_value(self) -> str:
        return self.get_setting("data").get("fits_facility_header_value")

    def get_fits_header_dateobs_keyword(self) -> str:
        return self.get_setting("data").get("fits_header_dateobs_keyword")

    def get_instruments(self) -> dict:
        return self.get_setting("instruments")

    def get_sites(self) -> dict:
        """
        Return an iterable of dictionaries that contain the information
        necessary to be used in the planning (visibility) tool.
        Format:
        {
            'Site Name': {
                'sitecode': 'tst',
                'latitude': -31.272,
                'longitude': 149.07,
                'elevation': 1116
            },
        }
        """
        return self.get_setting("sites")

    def get_weather_urls(self) -> dict:
        """Return a dictionary containing urls to check the weather for each site in your sites dictionary
        Format:
        {
            'code': 'REST',
            'sites': [
                {
                    'code': sitecode,
                    'weather_url': weather_url for site
                }
            ]
        }
        """
        # Why is every format different......
        # Basically restructure from generic dictionary to required format.
        weather_urls = {"code": self.facility_name, "sites": []}

        for site in self.get_setting("sites"):
            weather_urls["sites"].append(dict(self.get_setting("sites").get(site)))

        return weather_urls


def make_request(*args, **kwargs):
    response = requests.request(*args, **kwargs)
    if 401 <= response.status_code <= 403:
        raise ImproperCredentialsException("REST: " + str(response.content))
    elif 400 == response.status_code:
        raise forms.ValidationError(f"REST: {str(response.content)}")
    response.raise_for_status()
    return response


class RESTBaseForm(forms.Form):
    """The RESTBaseForm assumes nothing of fields, and just adds helper methods for
    loading field information from the settings."""

    def __init__(self, *args, **kwargs) -> None:
        if "facility_settings" not in kwargs:
            kwargs["facility_settings"] = RESTSettings("REST")
        self.facility_settings = kwargs.pop("facility_settings")
        super().__init__(*args, **kwargs)

    def get_instruments(self) -> dict:
        return self._get_instruments()

    def _get_instruments(self) -> dict:
        """Loads instruments from settings file and attempts to structure fields
        such that they are acceptable from a django form.

        :return dict: instrument information
        """
        # Might as well load all the form information here already. Then pop out the field as not needed?
        # Return a dictionary of the instruments.
        instruments = self.facility_settings.get_instruments()

        # Iterate through instruments.
        for instrument in instruments:
            # Check if instrument is a dictionary.
            if isinstance(instruments.get(instrument), dict):
                # Iterate through individual fields per instrument
                for key, value in instruments.get(instrument).items():
                    # Check if field is a dictionary, only fields are dictionaries, others are settings.
                    if isinstance(instruments.get(instrument).get(key), dict):
                        individual_field = dict(instruments.get(instrument).get(key))
                        field_type = individual_field.get("format")
                        individual_field.pop("format")

                        # TODO: Put these into a separate function
                        if "form" in individual_field:
                            individual_field.pop("form")

                        if "choice" in individual_field:
                            options = individual_field.get("choice")
                            individual_field.pop("choice")

                            choices = []

                            for individual_field_key in options:
                                single_choice = (
                                    individual_field_key,
                                    options.get(individual_field_key).get("name"),
                                )
                                choices.append(single_choice)

                            individual_field["choices"] = choices

                        getattr(self, "fields")[key] = self._choose_field(
                            field_type=field_type, **individual_field
                        )

        return instruments

    def _choose_field(self, field_type: str, *args, **kwargs):
        """Chooses django field type for form based on string.

        :param str field_type: string equivalent django form type
        :return django form class.
        """
        if field_type.capitalize() == "Boolean":
            return forms.BooleanField(*args, **kwargs)
        if field_type.capitalize() == "Char":
            return forms.CharField(*args, **kwargs)
        if field_type.capitalize() == "Choice":
            return forms.ChoiceField(*args, **kwargs)
        if field_type.capitalize() == "Float":
            return forms.FloatField(*args, **kwargs)
        if field_type.capitalize() == "Integer":
            return forms.IntegerField(*args, **kwargs)

    def proposal_choices(self):
        return


class RESTTemplateBaseForm(GenericTemplateForm, RESTBaseForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.get_instruments()

        for field_name in ["groups", "target_id"]:
            self.fields.pop(field_name, None)
        for field in self.fields:
            if field != "template_name":
                self.fields[field].required = False

        select_fields = dict(self.fields)
        select_fields.pop("template_name")

        self.helper.layout = Layout(
            self.common_layout,
            Div(
                Div(
                    *select_fields,
                    css_class="col",
                ),
                css_class="form-row",
            ),
        )


class RESTOptionalKeyValueLayout(Layout):
    def __init__(self, form_name, facility_settings, *args, **kwargs) -> None:
        self.facility_settings = facility_settings

    # TODO: Javascript to create arbitrary key:value as necessary.


class RESTObservationForm(BaseRoboticObservationForm, RESTBaseForm):
    """
    The RESTObservationForm attempts to create a form from the loaded settings.
    """

    def __init__(self, *args, **kwargs) -> None:
        # Need to load the facility_settings here even though it gets loaded in super __init__
        # So that we can modify the initial data before hitting the base __init__
        self.facility_settings = kwargs.get("facility_settings", RESTSettings("REST"))
        super().__init__(*args, **kwargs)

        instruments = self.get_instruments()

        unique_fields = dict(self.fields)
        for field_name in ["facility", "target_id", "observation_type"]:
            unique_fields.pop(field_name)

        self.helper.layout = Layout(
            self.common_layout,
            self.layout(unique_fields),
            self.button_layout(),
        )

    def button_layout(self) -> ButtonHolder:
        """
        Override Button layout from BaseObservationForm.
        """
        target_id = self.initial.get("target_id")

        return ButtonHolder(
            Submit(
                "submit",
                "Submit",
            ),
            HTML(
                f"""<a class="btn btn-outline-primary" href="{{% url 'tom_targets:detail' {target_id} %}}?tab=observe">
                        Back</a>"""
            ),
        )

    def form_name(self) -> str:
        return "base"

    def layout(self, unique_fields: dict = None) -> Div:
        # TODO: Iterate through fields and settings to programmatically create a grid for column/rows
        if unique_fields is None:
            unique_fields = self.fields
        return Div(
            Div(
                *unique_fields,
                css_class="col",
            ),
            css_class="form-row",
        )

    def optional_key_value_layout_class(self) -> RESTOptionalKeyValueLayout:
        return RESTOptionalKeyValueLayout

    def observation_payload(self) -> dict:
        payload = {}

        instruments = self.facility_settings.get_instruments()

        # Iterate through instruments.
        for instrument in instruments:
            # Check if instrument is a dictionary.
            if isinstance(instruments.get(instrument), dict):
                # Iterate through individual fields per instrument
                for key, value in instruments.get(instrument).items():
                    # Check if field is a dictionary, only fields are dictionaries, others are settings.
                    if isinstance(instruments.get(instrument).get(key), dict):
                        individual_field = dict(instruments.get(instrument).get(key))
                        individual_field.pop("format")

                        if "form" in individual_field:
                            individual_field.pop("form")

                        payload[key] = self.cleaned_data[key]

        target = Target.objects.get(pk=self.cleaned_data["target_id"])
        payload["ra"] = target.ra
        payload["dec"] = target.dec
        payload["name"] = target.name

        return payload


class RESTFacility(BaseRoboticObservationFacility):
    """
    The ``RESTFacility`` is the interface to an observatory which interfaces through a REST API.
    It attempts to create a standardisable interface.
    """

    name = "REST"
    observation_forms = {
        "ALL": RESTObservationForm,
    }

    def __init__(self, facility_settings=RESTSettings("REST")) -> None:
        self.facility_settings = facility_settings
        super().__init__()

    # TODO: this should be called get_form_class
    def get_form(self, observation_type):
        return self.observation_forms.get(observation_type, RESTObservationForm)

    # TODO: this should be called get_template_form_class
    def get_template_form(self, observation_type) -> RESTTemplateBaseForm:
        return RESTTemplateBaseForm

    def submit_observation(self, observation_payload: dict) -> list:
        """Submit observation based on form contents.

        :param dict observation_payload: contents to send to URL
        :return list: response from server.
        """
        response = make_request(
            "POST",
            self._construct_url("submit"),
            json=observation_payload,
        )

        if response.status_code not in [200, 304]:
            return []

        return [response.content]

    def validate_observation(self, observation_payload: dict):
        pass

    def cancel_observation(self, observation_payload: dict) -> bool:
        response = make_request(
            "POST",
            self._construct_url("cancel"),
            json=observation_payload,
        )
        # TODO: Figure out why this doesn't load

        return False

    def get_observation_url(self, observation_id: str) -> str:
        """Create observation URL from settings.
        Assumes that the observation URL is a function of the observation_id.

        :param str observation_id: observation_id that was initially returned from submit_observation
        :return str: complete observation URL
        """
        url_key = "observation"
        base_url = self._construct_url("", url_key=url_key)
        observation_url = base_url + f"/{observation_id}"
        return observation_url

    def get_date_obs_from_fits_header(self, header):
        return header.get(
            self.facility_settings.get_fits_header_dateobs_keyword(), None
        )

    def is_fits_facility(self, header) -> bool:
        """
        Returns True if the keyword is in the given FITS header and contains the value specified, False
        otherwise.

        :param header: FITS header object
        :type header: dictionary-like

        :returns: True if header matches your REST facility, False otherwise
        :rtype: boolean
        """
        return self.facility_settings.get_fits_facility_header_value() == header.get(
            self.facility_settings.get_fits_facility_header_keyword(), None
        )

    def get_start_end_keywords(self):
        return ("start", "end")

    def get_terminal_observing_states(self) -> list:
        return self.facility_settings.get_terminal_observing_states()

    def get_failed_observing_states(self) -> list:
        return self.facility_settings.get_failed_observing_states()

    def get_observing_sites(self) -> dict:
        return self.facility_settings.get_sites()

    def get_facility_weather_urls(self) -> dict:
        """
        `facility_weather_urls = {'code': 'XYZ', 'sites': [ site_dict, ... ]}`
        where
        `site_dict = {'code': 'XYZ', 'weather_url': 'http://path/to/weather'}`
        """
        return self.facility_settings.get_weather_urls()

    def get_facility_status(self) -> dict:
        """
        Get the telescope_states from the REST API endpoint and simply
        transform the returned JSON into the following dictionary hierarchy
        for use by the facility_status.html template partial.

        facility_dict = {'code': 'REST', 'sites': [ site_dict, ... ]}
        site_dict = {'code': 'XYZ', 'telescopes': [ telescope_dict, ... ]}
        telescope_dict = {'code': 'XYZ', 'status': 'AVAILABILITY'}

        Here's an example of the returned dictionary:

        literal_facility_status_example = {
            'code': 'REST',
            'sites': [
                {
                    'code': 'BPL',
                    'telescopes': [
                        {
                            'code': 'bpl.doma.1m0a',
                            'status': 'AVAILABLE'
                        },
                    ],
                },
                {
                    'code': 'ELP',
                    'telescopes': [
                        {
                            'code': 'elp.doma.1m0a',
                            'status': 'AVAILABLE'
                        },
                        {
                            'code': 'elp.domb.1m0a',
                            'status': 'AVAILABLE'
                        },
                    ]
                }
            ]
        }

        :return dict: facility_dict
        """
        facility_dict = {
            "code": self.name,
            "sites": [],
        }

        for site in self.facility_settings.get_setting("sites"):
            facility_dict["sites"].append(
                dict(self.facility_settings.get_setting("sites")[site])
            )
            # Most sites will not have multiple telescope so assume one
            # telescope per site and just duplicate the dictionary.

            # Take the last entry from the array since we just appended.
            facility_dict["sites"][-1]["telescopes"] = []

            # TODO: Figure out some sort of default method to check site/telescope availability.
            # Probably assume a status URL returning JSON and key in setting.
            facility_dict["sites"][-1]["telescopes"].append(
                dict(self.facility_settings.get_setting("sites")[site])
            )
        return facility_dict

    def get_observation_status(self, observation_id: str) -> dict:
        """Get the observation status from a URL.

        :param str observation_id: observation_id that was initially returned from submit_observation
        :return dict: state of the observation
        """
        response = make_request(
            "POST",
            self._construct_url("status"),
            json=observation_id,
        )
        status = response.json()["status"]

        return {"state": status, "scheduled_start": None, "scheduled_end": None}

    def data_products(self, observation_id, product_id=None) -> list:
        return []

    # The following methods are used internally by this module
    # and should not be called directly from outside code.

    def _construct_url(self, endpoint: str, url_key: str = "url") -> str:
        """Attempt to construct a URL from the given settings.

        :param str endpoint: which endpoint to select from settings
        :param str url_key: which url key to pick from settings, defaults to "url"
        :return str: Complete url
        """
        url_settings = self.facility_settings.get_setting(url_key)
        url_format = url_settings.get("format")
        url_parts = []

        for parts in url_format:
            if parts == "endpoint":
                next_part = url_settings.get("endpoint").get(endpoint)
            else:
                next_part = url_settings.get(parts)
            url_parts.append(next_part)

            final_url = "".join(url_parts)

        logger.info(f"Requested URL is {final_url}")

        return final_url
