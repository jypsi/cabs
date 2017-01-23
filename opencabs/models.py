from django.db import models
from django.conf import settings

import uuid
from hashlib import md5


class VehicleFeature(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=100, blank=True, default='')

    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class VehicleCategory(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=200, blank=True, default='')
    features = models.ManyToManyField(VehicleFeature)
    tariff_per_km = models.PositiveIntegerField()
    tariff_after_hours = models.PositiveIntegerField()

    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class Place(models.Model):
    name = models.CharField(max_length=100)

    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class Rate(models.Model):
    source = models.ForeignKey(Place, on_delete=models.CASCADE,
                               related_name='rate_source')
    destination = models.ForeignKey(Place, on_delete=models.CASCADE,
                                    related_name='rate_destination')
    vehicle_category = models.ForeignKey(VehicleCategory,
                                         on_delete=models.CASCADE,
                                         related_name='rate')
    oneway_price = models.PositiveIntegerField()
    driver_charge = models.PositiveIntegerField()

    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return '{}-{}'.format(self.source, self.destination)


class Booking(models.Model):
    source = models.ForeignKey(Place, on_delete=models.CASCADE,
                               related_name='booking_source')
    destination = models.ForeignKey(Place, on_delete=models.CASCADE,
                                    related_name='booking_destination')
    booking_type = models.CharField(choices=(('OW', 'One way'),
                                             ('RE', 'Rental')),
                                    max_length=2)
    travel_datetime = models.DateTimeField()
    vehicle_category = models.ForeignKey(VehicleCategory,
                                         on_delete=models.CASCADE,
                                         related_name='booking')
    customer_name = models.CharField(max_length=100)
    customer_mobile = models.CharField(max_length=20)

    status = models.CharField(choices=(('0', 'Request'),
                                       ('1', 'Confirmed'),
                                       ('2', 'Declined')),
                              max_length=1)
    pnr = models.CharField(max_length=20, blank=True, editable=False)

    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.pnr

    def save(self, *args, **kwargs):
        self.pnr = self._create_pnr()
        super().save(*args, **kwargs)

    def _create_pnr(self):
        text = '{}-{}-{}-{}-{}-{}-{}-{}'.format(
            self.source, self.destination, self.booking_type,
            self.travel_datetime, self.vehicle_category,
            self.customer_name, self.customer_mobile,
            uuid.uuid1())
        return settings.PNR_PREFIX + md5(text.encode('utf-8')).hexdigest()[:8]
