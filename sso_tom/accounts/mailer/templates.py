"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

# Templates for different emails
OBSERVATION_COMPLETED = dict()
OBSERVATION_COMPLETED["subject"] = (
    "[SSO Alerts] Notification - Observation status updated."
)
OBSERVATION_COMPLETED["message"] = (
    "<p>Dear {{first_name}} {{last_name}}: </p>"
    "<p>This is to let you know that your submitted observation has been updated. "
    "<p>"
    "Facility: {{facility}}<br />"
    "Target: {{target}}<br />"
    "Status: {{observation_status}}"
    "</p>"
    "<p> </p>"
    "<p>Regards, </p>"
    "<p>SSO Alerts Team</p>"
)
