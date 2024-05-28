# Copyright (c) 2024 Jamie Soon
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

import io
import logging
from sqlite3 import IntegrityError as SQL_IntegrityError

import fastavro
from django.contrib.auth.models import Group
from django.db.utils import IntegrityError as DJ_IntegrityError
from guardian.shortcuts import assign_perm
from psycopg2.errors import UniqueViolation
from tom_targets.models import Target, TargetList

logger = logging.getLogger(__name__)


# In reality, when stripped down all alerts will eventually be converted to a target.
# Therefore shoud be able to use the Generic Alert template but cannot.
# TODO: TOM backend needs to be further updated to treat this properly
from tom_alerts.alerts import GenericAlert


# class AvroAlert(GenericAlert):
class AvroAlert:
    def __init__(self, *args, **kwargs) -> None:
        # super().__init__(*args, **kwargs)
        pass

    def alert_logger(self, alert: dict) -> None:
        """Basic alert handler for an avro packet.

        :param dict alert: Dictionary containing alert data. See `consumer.poll`.
        """
        mytarget = self.process_message(alert)
        self.save_target(mytarget)

    def process_message(self, msg):
        """Process an avro message from Kafka.
        Have to choose an approximately default schema here.
        In this case it is chosen to be ZTF.
        https://zwickytransientfacility.github.io/ztf-avro-alert/schema.html

        :param confluent_kafka.Message msg: Object containing message information
        :return Target target: tom_toolkit Target class.
        """
        self.set_group_access(msg=msg)

        reader = fastavro.reader(io.BytesIO(msg.value()))
        schema = reader.schema

        # fastavro.reader returns an iterator?
        for record in reader:
            mytarget = Target(
                name=record["objectId"],
                type="SIDEREAL",
                ra=record["candidate"]["ra"],
                dec=record["candidate"]["dec"],
                epoch=record["candidate"]["jd"],
            )

        return mytarget

    def save_target(self, target: Target) -> None:
        """Try to save a target.

        :param Target target: tom_toolkit Target class.
        """
        try:
            target.save()
        except (UniqueViolation, SQL_IntegrityError, DJ_IntegrityError):
            logger.warning(f"Target {target} already in the database")
            pass

    def set_group_access(self, msg) -> None:
        # Define target list based on topics
        public_group, _ = Group.objects.get_or_create(name="Public")
        tl, is_created = TargetList.objects.get_or_create(name=msg.topic)
        assign_perm("tom_targets.view_targetlist", public_group, tl)
