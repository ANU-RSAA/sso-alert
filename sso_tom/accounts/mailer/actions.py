"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from django.urls import reverse

from . import templates, email


def email_observation_status_update(
    to_addresses, first_name, last_name, facility, target, observation_status
):
    """
    Sends out the email address verification email
    :param to_addresses: A list of addresses, in this case the user
    :param first_name: String
    :param last_name: String
    :param facility: String
    :param target: String - The target name
    :param observation_status: String
    :return: Nothing
    """

    # setting up the context
    context = {
        "first_name": first_name,
        "last_name": last_name,
        "facility": facility,
        "target": target,
        "observation_status": observation_status,
    }

    # Building and sending emails
    email.Email(
        subject=f"{templates.OBSERVATION_COMPLETED['subject']} :: {target}({facility})",
        to_addresses=to_addresses,
        template=templates.OBSERVATION_COMPLETED["message"],
        context=context,
    ).send_email()
