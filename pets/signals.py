from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Notification, PetRequest


@receiver(pre_save, sender=PetRequest)
def create_status_notification(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        previous = PetRequest.objects.get(pk=instance.pk)
    except PetRequest.DoesNotExist:
        return

    if previous.status != instance.status:
        Notification.objects.create(
            user=instance.user,
            pet_request=instance,
            message=f"Your {instance.request_type.lower()} pet report for {instance.breed} is now {instance.status}.",
        )
