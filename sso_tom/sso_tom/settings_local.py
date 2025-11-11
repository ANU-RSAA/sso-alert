from distutils.util import strtobool

from decouple import config as dotenv

# To add a new topic - add one here.
TOPICS = [
    'fink_early_sn_candidates_ztf',
    'fink_sn_candidates_ztf',
    'fink_sso_ztf_candidates_ztf',
    'fink_sso_fink_candidates_ztf',
    'fink_kn_candidates_ztf',
    'fink_early_kn_candidates_ztf',
    'fink_rate_based_kn_candidates_ztf',
    'fink_microlensing_candidates_ztf',
    'fink_blazar_ztf',
]


# Function to generate ALERT_STREAMS dynamically
def generate_alert_streams():
    return [
        {
            'ACTIVE': True,
            'NAME': 'tom_fink.alertstream.FinkAlertStream',
            'OPTIONS': {
                'URL': dotenv('FINK_CREDENTIAL_URL', default='set FINK_CREDENTIAL_URL value in environment'),
                'USERNAME': dotenv('FINK_CREDENTIAL_USERNAME',
                                   default='set FINK_CREDENTIAL_USERNAME value in environment'),
                'GROUP_ID': dotenv('FINK_CREDENTIAL_GROUP_ID',
                                   default='set FINK_CREDENTIAL_GROUP_ID value in environment'),
                'TOPIC': topic,
                'MAX_POLL_NUMBER': dotenv("FINK_MAX_POLL_NUMBER", default=1e10),
                'TIMEOUT': dotenv('FINK_TIMEOUT', default=10, cast=int),
                'TOPIC_HANDLERS': {
                    'fink.stream': 'sso_alerts.alert_handler.alert_logger',
                },
            },
        } for topic in TOPICS
    ]


# Generate ALERT_STREAMS dynamically
ALERT_STREAMS = generate_alert_streams()

SITE_URL = dotenv('SITE_URL', default='set SITE_URL value in environment')
SITE_DOMAIN_NAME = dotenv('SITE_DOMAIN_NAME', default='set SITE_DOMAIN_NAME value in environment')
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

DEVELOPMENT_MODE = bool(strtobool(dotenv('DEVELOPMENT_MODE', default='False')))

SERVER_EMAIL = dotenv('SERVER_EMAIL', default='set SERVER_EMAIL value in environment')
EMAIL_HOST = dotenv('EMAIL_HOST', default='set EMAIL_HOST value in environment')
EMAIL_FROM = dotenv('EMAIL_FROM', default='set EMAIL_FROM value in environment')
EMAIL_PORT = int(dotenv('EMAIL_PORT', default='set EMAIL_PORT value in environment'))

if DEVELOPMENT_MODE:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ANU_SITE = dotenv('ANU_SITE', default='set ANU_SITE value in environment')
PROPOSAL_DB_USERNAME = dotenv('ADACS_PROPOSALDB_TEST_USERNAME',
                              default='set ADACS_PROPOSALDB_TEST_USERNAME value in environment')
PROPOSAL_DB_PASSWORD = dotenv('ADACS_PROPOSALDB_TEST_PASSWORD',
                              default='set ADACS_PROPOSALDB_TEST_PASSWORD value in environment')
