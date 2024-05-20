from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from tom_observations.models import ObservationRecord

from .utils import submit_chain


@receiver(post_save, sender=ObservationRecord)
def observation_record_saved(sender, instance, created, **kwargs):
    """
    Signal handler for post-save of ObservationRecord instances.
    """
    if created:
        # TODO: if required we can do things here, at this stage nothing is required
        pass
    else:

        # finding if it is in a chain
        chained_observation = instance.observation_chain.first()

        # if in a chain, checking whether the condition is not met to trigger the next one
        if not chained_observation or instance.status not in chained_observation.trigger_next_condition:
            return

        # submit the chain, which will submit the unsubmitted one
        submit_chain(chained_observation.chain)

