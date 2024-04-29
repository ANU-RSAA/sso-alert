import uuid

import logging

import requests
from decouple import config

logger = logging.getLogger(__name__)

ADACS_PROPOSALDB_TEST_PASSWORD = config('ADACS_PROPOSALDB_TEST_PASSWORD')
ADACS_PROPOSALDB_TEST_USERNAME = config('ADACS_PROPOSALDB_TEST_USERNAME')
print(f"TOKENS FOR ACCESS {ADACS_PROPOSALDB_TEST_PASSWORD} {ADACS_PROPOSALDB_TEST_USERNAME}")


def submit_observation_anu230cm(observation_payload):
    """
    This method takes in the serialized data from the form and actually
    submits the observation to the remote api
    """
    # Add ANU2.3m API query here.
    test_anu230cm_emulator = True
    if test_anu230cm_emulator:
        print("new submit_observation_payload")
        # local version of emuldate_common
        emulate_ANU230cm = "https://mortal.anu.edu.au/aocs/"
        # url_suffix = "/"
        url_suffix = ".php"
        # Keyword dictionary
        PROPOSAL = "PROPOSAL"
        USERDEFID = "USERDEFID"
        USERDEFPRI = "USERDEFPRI"
        NOBSBLK = "NOBSBLK"

        MAXSEEING = "MAXSEEING"
        PHOTOMETRIC = "PHOTOMETRIC"
        MAXLUNARPHASE = "MAXLUNARPHASE"
        TIMECONSTRAINT = "TIMECONSTRAINT"
        TIMEREF = "TIMEREF"
        TIMEWINDOW = "TIMEWINDOW"

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
        url = emulate_ANU230cm + '/addobsblockexec' + url_suffix

        post_data = {}
        post_data[PROPOSAL] = observation_payload['params']['proposal']

        print(observation_payload)

        post_data[USERDEFID] = observation_payload['params']['userdefid']
        post_data[USERDEFPRI] = observation_payload['params']['userdefpri']
        post_data[NOBSBLK] = 1
        post_data[MAXSEEING] = observation_payload['params']['maxseeing']
        post_data[PHOTOMETRIC] = observation_payload['params']['photometric']
        post_data[MAXLUNARPHASE] = observation_payload['params']['maxlunarphase']
        post_data[TIMECONSTRAINT] = observation_payload['params']['timeconstraint']
        post_data[TIMEREF] = observation_payload['params']['timeref']
        post_data[TIMEWINDOW] = observation_payload['params']['timewindow']
        post_data[INSTR_PRI_ + "0"] = observation_payload['params']['instr_pri_0']
        post_data[IMGTYPE_ + "0"] = observation_payload['params']['imgtype_0']
        post_data[MODE_ + "0"] = observation_payload['params']['mode_0']
        post_data[DICHROIC_ + "0"] = observation_payload['params']['dichroic_0']
        post_data[RED_GRATING_ + "0"] = observation_payload['params']['red_grating_0']  # ?
        post_data[BLUE_GRATING_ + "0"] = observation_payload['params']['blue_grating_0']
        post_data[APERTUREWHEEL_ + "0"] = observation_payload['params']['aperturewheel_0']
        post_data[RA_ + "0"] = observation_payload['params']['ra_0']
        post_data[DEC_ + "0"] = observation_payload['params']['dec_0']
        post_data[PMOT_ + "0"] = observation_payload['params']['pmot_0']
        post_data[ACQ_RA_ + "0"] = observation_payload['params']['acq_ra_0']
        post_data[ACQ_DEC_ + "0"] = observation_payload['params']['acq_dec_0']
        post_data[ACQ_PMOT_ + "0"] = observation_payload['params']['acq_pmot_0']
        post_data[BLINDACQ_ + "0"] = observation_payload['params']['blindacq_0']
        post_data[ROT_ + "0"] = observation_payload['params']['rot_0']
        post_data[ROTANG_ + "0"] = observation_payload['params']['rotang_0']
        post_data[MAG_ + "0"] = observation_payload['params']['mag_0']
        post_data[AGFILTER_ + "0"] = observation_payload['params']['agfilter_0']
        post_data[GUIDE_ + "0"] = observation_payload['params']['guide_0']
        post_data[NEXP_ + "0"] = observation_payload['params']['nexp_0']
        post_data[STELLAR_ + "0"] = observation_payload['params']['stellar_0']
        post_data[BINX_ + "0"] = observation_payload['params']['binx_0']
        post_data[BINY_ + "0"] = observation_payload['params']['biny_0']
        post_data[EXPTIME_ + "0"] = observation_payload['params']['exptime_0']
        post_data[SKY_EXPTIME_ + "0"] = observation_payload['params']['sky_exptime_0']
        post_data[SCDESCR_ + "0"] = observation_payload['params']['scdescr_0']
        post_data[SKYA_RA_ + "0"] = observation_payload['params']['skya_ra_0']
        post_data[SKYA_DEC_ + "0"] = observation_payload['params']['skya_dec_0']
        #
        response = requests.post(url, data=post_data,
                                 auth=(ADACS_PROPOSALDB_TEST_USERNAME, ADACS_PROPOSALDB_TEST_PASSWORD))
        print(f"{response}")

        try:
            # content = json.loads(response.content)
            print(f"json response={response.content}")
        except Exception:
            msg = f"Bad response"
            logger.exception(msg)

        return [f"{post_data[PROPOSAL]}-{post_data[USERDEFID]}"]
    return [uuid.uuid4()]  # update it to unique
