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

import logging
import uuid

from confluent_kafka import Consumer, KafkaError
from django.conf import settings
from tom_alertstreams.alertstreams.alertstream import AlertStream

logger = logging.getLogger(__name__)


class KafkaAlertStream(AlertStream):
    """Poll alerts from an arbitrary Kafka Alert Stream"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.config["error_cb"] = self.error_callback

        if "group.id" not in self.config:
            self.config["group.id"] = str(uuid.uuid4())

    def error_callback(self, err):
        if err.code() == KafkaError._TRANSPORT:
            logger.error(
                f"KafkaError: Unable to connect to Kafka broker at {self.config['bootstrap.servers']}\n"
                f"Is the broker running?"
            )

    def listen(self):
        """Listen to one topic from an Apache Kafka stream"""
        consumer = Consumer(self.config)
        consumer.subscribe(list(self.topic_handlers.keys()))

        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            kafka_error = msg.error()  # cimpl.KafkaError
            if kafka_error is None:
                # no error, so call the alert handler
                topic = msg.topic()
                try:
                    self.alert_handler[topic](msg)
                except KeyError as err:
                    logger.error(
                        f"Alert from topic {topic} received but no handler defined. err: {err}"
                    )
            else:
                logger.error(f"KafkaError: {kafka_error.name()}: {kafka_error.str()}")
        consumer.close()
