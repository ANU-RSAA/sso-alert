import time
import logging
import traceback

from django.contrib.auth import get_user_model
from fink_client.consumer import AlertConsumer

from tom_alertstreams.alertstreams.alertstream import AlertStream
from tom_targets.models import Target, TargetList

from psycopg2.errors import UniqueViolation
from django.db.utils import IntegrityError as DJ_IntegrityError
from sqlite3 import IntegrityError as SQL_IntegrityError
from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm, get_user_perms

from .models import AlertStreams
from sso_tom.utils import submit_observation_from_template
from chained.utils import create_chain_and_submit_first

logger = logging.getLogger(__name__)


def give_user_access_to_target(target, topic):

    alert_streams = AlertStreams.objects.filter(topic=topic)

    for alert_stream in alert_streams:
        if not get_user_perms(alert_stream.user, target).filter(codename='view_target').exists():
            target.give_user_access(user=alert_stream.user)

        if alert_stream.automatic_observability:
            if alert_stream.template_observation:
                submit_observation_from_template(
                    target=target,
                    template=alert_stream.template_observation,
                    user=alert_stream.user,
                )
            elif alert_stream.template_chained:
                create_chain_and_submit_first(
                    target=target,
                    template_chained=alert_stream.template_chained,
                    user=alert_stream.user,
                    topic=alert_stream.topic,
                )


def alert_logger(alert, topic):
    """Basic alert handler for Fink

    This alert handler simply display on screen basic information,
    and save the alert as a new Target.

    Parameters
    ----------
    alert: dic
        Dictionary containing alert data. See `consumer.poll`.
    topic: str
        Topic name

    Warnings
    ----------
    UniqueViolation, SQL_IntegrityError, DJ_IntegrityError
        If the target is already saved

    Raises
    ----------
    Exception (base)
        for any other failures than name clash when
        saving the target in the database.

    """
    print("custom logger##################################\n")
    utc = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    logger.info("fink.alert_logger topic: {}".format(topic))
    logger.info(
        "fink.alert_logger value: {} emitted {} (received {})".format(
            alert["objectId"], alert["timestamp"], utc
        )
    )

    mytarget = Target(
        name=alert["objectId"],
        type="SIDEREAL",
        ra=alert["candidate"]["ra"],
        dec=alert["candidate"]["dec"],
        epoch=alert["candidate"]["jd"],
    )

    try:
        mytarget.save(
            extras={
                "fink broker link": "https://fink-portal.org/{}".format(
                    alert["objectId"]
                )
            }
        )
    except (UniqueViolation, SQL_IntegrityError, DJ_IntegrityError):
        logger.warning(f"Target {mytarget} already in the database")
        pass
    except Exception:
        logger.error("error when trying to save new alerts in the db", exc_info=1)
        logger.error(traceback.format_exc())

    give_user_access_to_target(target=mytarget, topic=topic)
