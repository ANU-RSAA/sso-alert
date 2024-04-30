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

from datetime import datetime
import logging

from django import forms

from tom_common.exceptions import ImproperCredentialsException
from tom_observations.models import ObservationRecord
from tom_targets.models import (
    Target,
)

from .rest import (
    RESTTemplateBaseForm,
    RESTObservationForm,
    RESTSettings,
    RESTFacility,
    make_request,
)

logger = logging.getLogger(__name__)


class DREAMSSettings(RESTSettings):
    """DREAMS Specific settings"""

    def __init__(self, facility_name="DREAMS") -> None:
        super().__init__(facility_name=facility_name)


class DREAMSTemplateBaseForm(RESTTemplateBaseForm):
    def __init__(self, *args, **kwargs) -> None:
        if "facility_settings" not in kwargs:
            kwargs["facility_settings"] = DREAMSSettings("DREAMS")
        super().__init__(*args, **kwargs)


class DREAMSObservationForm(RESTObservationForm):
    def __init__(self, *args, **kwargs) -> None:
        if "facility_settings" not in kwargs:
            kwargs["facility_settings"] = DREAMSSettings("DREAMS")
        super().__init__(*args, **kwargs)

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

        now = datetime.now().strftime("%Y%m%dT%H%M%S")
        payload["user_defined_id"] = f"{now}_{payload['proposal']}_{target.name}"

        # TODO: Save API key to TOM account and load from there.
        return payload


class DREAMSFacility(RESTFacility):
    """
    The ``DREAMSFacility`` is the interface to DREAMS
    """

    name = "DREAMS"
    observation_forms = {
        "IMAGING": DREAMSObservationForm,
    }

    def __init__(self, facility_settings=DREAMSSettings("DREAMS")) -> None:
        super().__init__(facility_settings=facility_settings)

    # TODO: this should be called get_form_class
    def get_form(self, observation_type):
        return self.observation_forms.get(observation_type, DREAMSObservationForm)

    # TODO: this should be called get_template_form_class
    def get_template_form(self, observation_type) -> DREAMSTemplateBaseForm:
        return DREAMSTemplateBaseForm

    def submit_observation(self, observation_payload: dict) -> list:
        response = make_request(
            "POST",
            self._construct_url("submit"),
            data=observation_payload,
        )

        if response.status_code not in [200, 304]:
            return []

        content = response.json()
        if not (content.get("authenticated") and content.get("authorised")):
            # TODO: Add another exception to tom_common to properly explain this instead of the settings.
            raise ImproperCredentialsException(f"{self.name}: {content.get('msg')}")

        if not content.get("status"):
            # TODO: Create exception within tom to raise this as an error within the form itself?
            raise forms.ValidationError(f"{self.name}: {content.get('msg')}")

        return [observation_payload.get("user_defined_id")]

    def get_observation_status(self, observation_id: str) -> dict:
        observation_payload = {"user_defined_id": observation_id}

        # Retrieve parameters that were passed as part of the initial observation request
        parameters = ObservationRecord.objects.get(
            observation_id=observation_id
        ).parameters

        observation_payload["proposal"] = parameters.get("proposal")
        observation_payload["key"] = parameters.get("key")

        response = make_request(
            "POST",
            self._construct_url("status"),
            data=observation_payload,
        )

        status = response.json().get("status")

        return {"state": status, "scheduled_start": None, "scheduled_end": None}

    def get_observation_url(self, observation_id: str) -> str:
        url_key = "observation"
        base_url = self._construct_url("", url_key=url_key)
        key = self.facility_settings.get_setting(url_key).get("key").get("observation")

        # Retrieve target associated with the observation record
        target_name = ObservationRecord.objects.get(
            observation_id=observation_id
        ).target

        observation_url = base_url + f"{key}={target_name}"

        return observation_url
