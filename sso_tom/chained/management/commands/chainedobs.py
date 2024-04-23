from django.core.management.base import BaseCommand, CommandError

from datetime import datetime, timedelta
from dateutil.parser import parse
import logging
import traceback

from tom_observations.cadence import BaseCadenceForm, CadenceStrategy
from tom_observations.models import ObservationRecord
from tom_observations.models import ObservationGroup
from tom_observations.facility import get_service_class

from tom_observations.cadence import get_cadence_strategy
from tom_observations.models import DynamicCadence
from tom_targets.models import Target

logger = logging.getLogger(__name__)
    
class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        #parser.add_argument("poll_ids", nargs="+", type=int)
        pass

    def handle(self, *args, **options):
        print(f" HANDLE COMMAND ")
        do_create = False
        if do_create:
            ## Create some
            target = Target.objects.filter(name="A112t8b")
            print(f"target={target[0].id}")
            obs_params = {}
            obs_params['target_id'] = target[0].id
            obs_params['start'] = (datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M:%S')
            obs_params['end'] = (datetime.now() + timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M:%S')
            self.group = ObservationGroup.objects.filter(name="pretty pictures")
            #observing_records = ObservingRecordFactory.create_batch(5,
            #                                                        target_id=target.id,
            #                                                        parameters=obs_params)
            #self.group = ObservationGroup.objects.create()
            #self.group.observation_records.add(*observing_records)
            #self.group.save()
            self.dynamic_cadence = DynamicCadence.objects.create(
                cadence_strategy='Test Strategy', cadence_parameters={'cadence_frequency': 72}, active=True,
                observation_group=self.group[0])
            self.dynamic_cadence.save()

            if True:
                return
        else:
            cadenced_groups = DynamicCadence.objects.filter(active=True)

            updated_cadences = []

            for cg in cadenced_groups:
                try:
                    print(f"TRY {cg.cadence_strategy}")
                    strategy = get_cadence_strategy(cg.cadence_strategy)(cg)
                    print(f" about to run on {strategy}?")
                    try:
                        new_observations = strategy.run()
                    except Exception as e:
                        logger.error((f'Unable to run cadence_group: {cg}; strategy {strategy};'
                                    f' with id {cg.id} due to error: {e}'))
                        logger.error(f'{traceback.format_exc()}')
                        continue
                    if not new_observations:
                        logger.log(msg=f'No changes from dynamic cadence {cg}', level=logging.INFO)
                    else:
                        logger.log(msg=f'''Cadence update completed for dynamic cadence {cg},
                                        {len(new_observations)} new observations created.''',
                                level=logging.INFO)
                        updated_cadences.append(cg.observation_group)
                except Exception as e:
                    logger.error(msg=f'Unable to run strategy {cg} with id {cg.id} due to error: {e}')

            if updated_cadences:
                msg = 'Created new observations for dynamic cadences with observation groups: {0}.'
                return msg.format(', '.join([str(cg) for cg in updated_cadences]))
            else:
                return 'No new observations for any dynamic cadences.'