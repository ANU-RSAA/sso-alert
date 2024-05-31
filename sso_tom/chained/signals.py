from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from tom_observations.models import ObservationRecord

from .utils import submit_chain
from accounts.mailer.actions import email_observation_status_update


@receiver(pre_save, sender=ObservationRecord)
def observation_record_pre_save(sender, instance, **kwargs):
    """
    Signal handler for pre-save of ObservationRecord instances.
    Stores the previous status for later comparison in post-save.
    """
    if instance.pk:
        previous_instance = ObservationRecord.objects.get(pk=instance.pk)
        instance._previous_status = previous_instance.status
    else:
        instance._previous_status = None


@receiver(post_save, sender=ObservationRecord)
def observation_record_saved(sender, instance, created, **kwargs):
    """
    Signal handler for post-save of ObservationRecord instances.
    """
    if created:
        # TODO: if required we can do things here, at this stage nothing is required
        pass
    else:
        if hasattr(instance, '_previous_status') and instance._previous_status != instance.status:

            # send out email
            try:
                email_observation_status_update(
                    to_addresses=[instance.user.email],
                    first_name=instance.user.first_name,
                    last_name=instance.user.last_name,
                    facility=instance.facility,
                    target=instance.target,
                    observation_status=instance.status,
                )
            except Exception as e:
                pass

            # finding if it is in a chain
            chained_observation = instance.observation_chain.first()

            # if in a chain, checking whether the condition is not met to trigger the next one
            if not chained_observation or instance.status not in chained_observation.trigger_next_condition:
                return

            # submit the chain, which will submit the unsubmitted one
            submit_chain(chained_observation.chain)
