from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from finance.models import Payment

from .models import BookingVehicle


@receiver([post_save, post_delete], sender=Payment)
def update_booking_payment_info(sender, instance, **kwargs):
    if instance.item_content_type.app_label == 'opencabs' and \
            instance.item_content_type.model == 'booking':
        if instance.item_object:
            instance.item_object.save()


@receiver([post_save, post_delete], sender=BookingVehicle)
def update_booking_drivers(sender, instance, **kwargs):
    instance.booking.update_drivers()
