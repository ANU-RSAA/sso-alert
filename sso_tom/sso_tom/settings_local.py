# Copyright (c) 2025 SSO Alert System/RSAA
#
# This file is part of TOM Toolkit/SSO-Alert
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

# This file is for parsing specific local settings.


from decouple import config as dotenv
from decouple import strtobool

### SITE SETTINGS ###
SITE_URL = dotenv("SITE_URL", default="set SITE_URL value in environment")
SITE_DOMAIN_NAME = dotenv(
    "SITE_DOMAIN_NAME", default="set SITE_DOMAIN_NAME value in environment"
)
print(f"WE SET SITE_URL TO {SITE_URL}. Update ALLOWED_HOSTS")

ALLOWED_HOSTS = [
    ".localhost",
    "127.0.0.1",
    "[::1]",
    "10.0.0.24",
    SITE_DOMAIN_NAME,
]
CSRF_TRUSTED_ORIGINS = [SITE_URL]
print(f"WE SET ALLOWED_HOSTS TO {ALLOWED_HOSTS}")
print(f"WE SET CSRF_TRUSTED_ORIGINS TO {CSRF_TRUSTED_ORIGINS}")
### END SITE SETTINGS ###


### ANU 2.3M SETTINGS ###
ANU_SITE = dotenv("2M3_SITE", default="set 2M3_SITE value in environment")
PROPOSAL_DB_USERNAME = dotenv(
    "2M3_USERNAME", default="set 2M3_USERNAME value in environment"
)
PROPOSAL_DB_PASSWORD = dotenv(
    "2M3_PASSWORD", default="set 2M3_PASSWORD value in environment"
)
ARCHIVE_2M3_QUERY = dotenv("2M3_ARCHIVE_QUERY", default=None)
ARCHIVE_2M3_RESULTS = dotenv("2M3_ARCHIVE_RESULTS", default=None)
### END ANU 2.3M SETTINGS ###


### ALERT STREAMS SETTINGS ###

#### FINK SETTINGS ####
USE_FINK = bool(strtobool(dotenv("USE_FINK", default="False")))

# To add a new topic - add one here.
ZTF_TOPICS = [
    "fink_early_sn_candidates_ztf",
    "fink_sn_candidates_ztf",
    "fink_sso_ztf_candidates_ztf",
    "fink_sso_fink_candidates_ztf",
    "fink_kn_candidates_ztf",
    "fink_early_kn_candidates_ztf",
    "fink_rate_based_kn_candidates_ztf",
    "fink_microlensing_candidates_ztf",
    "fink_blazar_ztf",
]

LSST_TOPICS = [
    "fink_extragalactic_candidate_lsst",
    "fink_cataloged_lsst",
    "fink_in_tns_lsst",
]

TOPICS = ZTF_TOPICS + LSST_TOPICS

if USE_FINK:
    if dotenv("FINK_CREDENTIAL_URL", default=None) is not None:
        finkZTFTopics = [
            {
                "ACTIVE": True,
                "NAME": "tom_fink.alertstream.FinkAlertStream",
                "OPTIONS": {
                    "URL": dotenv(
                        "FINK_CREDENTIAL_URL",
                        default="set FINK_CREDENTIAL_URL value in environment",
                    ),
                    "USERNAME": dotenv(
                        "FINK_CREDENTIAL_USERNAME",
                        default="set FINK_CREDENTIAL_USERNAME value in environment",
                    ),
                    "GROUP_ID": dotenv(
                        "FINK_CREDENTIAL_GROUP_ID",
                        default="set FINK_CREDENTIAL_GROUP_ID value in environment",
                    ),
                    "TOPIC": topic,
                    "MAX_POLL_NUMBER": dotenv("FINK_MAX_POLL_NUMBER", default=1e10),
                    "TIMEOUT": dotenv("FINK_TIMEOUT", default=10, cast=int),
                    "TOPIC_HANDLERS": {
                        "fink.stream": "sso_alerts.alert_handler.alert_logger",
                    },
                },
            }
            for topic in ZTF_TOPICS
        ]
    if dotenv("FINK_CREDENTIAL_LSST_URL", default=None) is not None:
        finkLSSTTopics = [
            {
                "ACTIVE": True,
                "NAME": "tom_fink.alertstream.FinkAlertStream",
                "OPTIONS": {
                    "URL": dotenv(
                        "FINK_CREDENTIAL_LSST_URL",
                        default="set FINK_CREDENTIAL_LSST_URL value in environment",
                    ),
                    "USERNAME": dotenv(
                        "FINK_CREDENTIAL_USERNAME",
                        default="set FINK_CREDENTIAL_USERNAME value in environment",
                    ),
                    "GROUP_ID": dotenv(
                        "FINK_CREDENTIAL_GROUP_ID",
                        default="set FINK_CREDENTIAL_GROUP_ID value in environment",
                    ),
                    "TOPIC": topic,
                    "MAX_POLL_NUMBER": dotenv("FINK_MAX_POLL_NUMBER", default=1e10),
                    "TIMEOUT": dotenv("FINK_TIMEOUT", default=10, cast=int),
                    "TOPIC_HANDLERS": {
                        "fink.stream": "sso_alerts.alert_handler.alert_logger_lsst",
                    },
                },
            }
            for topic in LSST_TOPICS
        ]


# Function to generate ALERT_STREAMS dynamically
def generate_alert_streams():
    ALL_STREAMS = []
    if USE_FINK:
        if dotenv("FINK_CREDENTIAL_URL", default=None) is not None:
            ALL_STREAMS = ALL_STREAMS + finkZTFTopics
        if dotenv("FINK_CREDENTIAL_LSST_URL", default=None) is not None:
            ALL_STREAMS = ALL_STREAMS + finkLSSTTopics
    return ALL_STREAMS


# Generate ALERT_STREAMS dynamically
ALERT_STREAMS = generate_alert_streams()
### END ALERT STREAMS SETTINGS ###

### EMAIL SETTINGS ###
SERVER_EMAIL = dotenv("SERVER_EMAIL", default="set SERVER_EMAIL value in environment")
EMAIL_HOST = dotenv("EMAIL_HOST", default="set EMAIL_HOST value in environment")
EMAIL_FROM = dotenv("EMAIL_FROM", default="set EMAIL_FROM value in environment")
EMAIL_PORT = int(dotenv("EMAIL_PORT", default="set EMAIL_PORT value in environment"))

USE_SMTP = bool(strtobool(dotenv("USE_SMTP", default="False")))

if USE_SMTP:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
### END EMAIL SETTINGS ###

### SKY SETTINGS ###
SKY_DATA_PATH = dotenv(
    "SKY_DATA_PATH", default="set SKY_DATA_PATH value in environment"
)
### END SKY SETTINGS ###
