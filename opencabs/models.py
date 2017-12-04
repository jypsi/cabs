from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone

from finance.models import Payment

import json
import uuid
from io import StringIO
from hashlib import md5
from datetime import datetime
from collections import OrderedDict

from utils.pdf import draw_pdf


class VehicleFeature(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=100, blank=True, default='')

    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class VehicleCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(max_length=200, blank=True, default='')

    def __str__(self):
        return self.name


class VehicleRateCategory(models.Model):
    name = models.CharField(max_length=30, db_index=True, unique=True)
    description = models.TextField(max_length=200, blank=True, default='')
    category = models.ForeignKey(VehicleCategory, db_index=True)
    features = models.ManyToManyField(VehicleFeature, blank=True)
    tariff_per_km = models.PositiveIntegerField()
    tariff_after_hours = models.PositiveIntegerField()

    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        unique_together = ('name', 'category')

    def __str__(self):
        return self.name


class Place(models.Model):
    name = models.CharField(max_length=100, db_index=True, unique=True)

    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class Rate(models.Model):
    source = models.ForeignKey(Place, on_delete=models.CASCADE,
                               related_name='rate_source')
    destination = models.ForeignKey(Place, on_delete=models.CASCADE,
                                    related_name='rate_destination')
    vehicle_category = models.ForeignKey(VehicleRateCategory,
                                         on_delete=models.CASCADE,
                                         related_name='rate', db_index=True)
    oneway_price = models.PositiveIntegerField()
    oneway_distance = models.PositiveIntegerField(default=0, blank=True)
    oneway_driver_charge = models.PositiveIntegerField()

    roundtrip_price = models.PositiveIntegerField(blank=True, default=0)
    roundtrip_distance = models.PositiveIntegerField(blank=True, default=0)
    roundtrip_driver_charge = models.PositiveIntegerField(
        blank=True, default=0)

    code = models.CharField(max_length=100, editable=False, blank=True,
                            db_index=True)

    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        unique_together = ('code', 'vehicle_category')

    def __str__(self):
        return '{}-{}'.format(self.source, self.destination)

    def save(self, *args, **kwargs):
        self.code = settings.ROUTE_CODE_FUNC(
            self.source.name, self.destination.name)
        if not self.roundtrip_price:
            self.roundtrip_price = 2 * self.oneway_price
        if not self.roundtrip_driver_charge:
            self.roundtrip_driver_charge = 2 * self.oneway_driver_charge
        if not self.roundtrip_distance:
            self.roundtrip_distance = 2 * self.roundtrip_distance
        super().save(*args, **kwargs)


class Driver(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    mobile = models.CharField(max_length=20, unique=True, db_index=True)

    def __str__(self):
        return '{}/{}'.format(self.name, self.mobile)


class Vehicle(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    number = models.CharField(max_length=20, unique=True, db_index=True)
    category = models.ForeignKey(
        VehicleCategory,
        on_delete=models.CASCADE)
    driver = models.OneToOneField(
        Driver,
        on_delete=models.CASCADE,
        unique=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return '{}/{}'.format(self.name, self.number)


BOOKING_TYPE_CHOICES_DICT = OrderedDict(
    (
        ('OW', 'One way'),
        ('RT', 'Round trip')
    )
)
BOOKING_STATUS_CHOICES_DICT = OrderedDict(
    (
        ('0', 'Request'),
        ('1', 'Confirmed'),
        ('2', 'Declined')
    )
)
BOOKING_PAYMENT_STATUS_CHOICES_DICT = OrderedDict(
    (
        ('NP', 'Not paid'),
        ('PR', 'Partial'),
        ('PD', 'Paid'),
    )
)


class Booking(models.Model):
    source = models.ForeignKey(Place, on_delete=models.CASCADE,
                               related_name='booking_source')
    destination = models.ForeignKey(Place, on_delete=models.CASCADE,
                                    related_name='booking_destination')
    pickup_point = models.TextField(max_length=200, blank=True, default="")
    booking_type = models.CharField(choices=BOOKING_TYPE_CHOICES_DICT.items(),
                                    max_length=2)
    travel_date = models.DateField()
    travel_time = models.TimeField()
    vehicle_type = models.ForeignKey(VehicleRateCategory,
                                     on_delete=models.CASCADE,
                                     related_name='booking')
    customer_name = models.CharField(max_length=100, db_index=True,
                                     verbose_name='Name')
    customer_mobile = models.CharField(max_length=20, default='', blank=True,
                                       db_index=True, verbose_name='Mobile')
    customer_email = models.EmailField(default='', blank=True, db_index=True,
                                       verbose_name='Email')
    ssr = models.TextField(verbose_name='Special service request',
                           max_length=200, blank=True, default="",
                           help_text="Special service request")

    status = models.CharField(choices=BOOKING_STATUS_CHOICES_DICT.items(),
                              max_length=1,
                              default='0')
    payment_status = models.CharField(
        choices=BOOKING_PAYMENT_STATUS_CHOICES_DICT.items(), max_length=3,
        blank=True, null=True, default='NP')
    payment_done = models.PositiveIntegerField(blank=True, default=0)
    payment_due = models.PositiveIntegerField(blank=True, default=0)
    revenue = models.PositiveIntegerField(blank=True, default=0)
    last_payment_date = models.DateTimeField(blank=True, null=True)
    accounts_verified = models.BooleanField(default=False, db_index=True)
    payments = GenericRelation(Payment,
                               content_type_field='item_content_type',
                               object_id_field='item_object_id',
                               related_query_name='bookings')

    driver_paid = models.BooleanField(default=False)
    driver_pay = models.PositiveIntegerField(blank=True, default=0)
    driver_invoice_id = models.CharField(max_length=50, blank=True)

    vehicle = models.ForeignKey(Vehicle, blank=True, null=True)
    driver = models.ForeignKey(Driver, blank=True, null=True)
    extra_info = models.TextField(blank=True, default='')
    booking_id = models.CharField(max_length=20, blank=True, editable=False,
                                  db_index=True, unique=True)

    total_fare = models.PositiveIntegerField(blank=True, default=0)
    fare_details = models.TextField(blank=True, default="{}")
    distance = models.PositiveIntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.booking_id

    @property
    def booking_type_display(self):
        return BOOKING_TYPE_CHOICES_DICT.get(self.booking_type)

    def save(self, *args, **kwargs):
        if not self.customer_email and not self.customer_mobile:
            raise ValidationError('Either of customer email and mobile is '
                                  'mandatory.')
        if self.id is None:
            self.booking_id = self._create_booking_id()
            rate = self.vehicle_type.rate.get(
                code=settings.ROUTE_CODE_FUNC(self.source.name,
                                              self.destination.name))
            fare_details = {
                'tariff_per_km': self.vehicle_type.tariff_per_km,
                'after_hour_charges': self.vehicle_type.tariff_after_hours,
                'price': (rate.oneway_price if self.booking_type == 'OW' else
                          rate.roundtrip_price),
                'driver_charge': (rate.oneway_driver_charge
                                  if self.booking_type == 'OW' else
                                  rate.roundtrip_driver_charge)
            }
            if timezone.now().timestamp() >= datetime.strptime(
                    settings.EXTRA_TAXES_FROM_DATETIME,
                    settings.DATETIME_STR_FORMAT).timestamp():
                fare_details['taxes'] = {
                    k: v['rate'] * fare_details[settings.TAXABLE_FIELD]
                    for k, v in settings.TAXES.items()}
                fare_details['taxes']['total'] = sum(
                    [fare_details['taxes'][k] for k in settings.TAXES])
                fare_details['total'] = fare_details['price'] + fare_details[
                'taxes']['total']
            else:
                fare_details['total'] = fare_details['price']
            self.total_fare = fare_details['total']
            self.payment_due = self.total_fare - self.payment_done
            self.fare_details = json.dumps(fare_details)

        if self.vehicle and not self.driver:
            self.driver = self.vehicle.driver

        if self.id and self.driver_paid:
            self.pay_to_driver()

        super().save(*args, **kwargs)

    def _create_booking_id(self):
        text = '{}-{}-{}-{}-{}-{}-{}-{}-{}'.format(
            self.source, self.destination, self.booking_type,
            self.travel_date, self.travel_time, self.vehicle,
            self.customer_name, self.customer_mobile,
            uuid.uuid1())
        return (settings.BOOKING_ID_PREFIX + md5(
            text.encode('utf-8')).hexdigest()[:8]).upper()

    def update_payment_summary(self):
        payment_done = 0
        expenses = 0
        last_payment_date = None

        for payment in self.payments.all().order_by('timestamp'):
            if payment.type == 1:
                payment_done += payment.amount.amount
            else:
                expenses += payment.amount.amount
            last_payment_date = payment.timestamp

        self.last_payment_date = last_payment_date
        self.payment_done = payment_done
        self.payment_due = self.total_fare - self.payment_done
        if self.payment_due > 0:
            self.payment_status = 'PR'
        else:
            self.payment_status = 'PD'

        self.revenue = payment_done - expenses

        self.save()

    def pay_to_driver(self):
        fare_details = json.loads(self.fare_details)
        payment, created = Payment.objects.get_or_create(
            item_content_type__app_label='opencabs',
            item_content_type__model='booking',
            item_object_id=self.id,
            comment__startswith='Paid to driver',
            defaults={
                'item_object': self,
                'amount': fare_details['driver_charge'],
                'comment': "Paid to driver: %s" % self.driver,
                'type': -1
            }
        )
        self.driver_pay = fare_details['driver_charge']
        self.driver_invoice_id = payment.invoice_id

    def invoice(self):
        customer_details = [self.customer_name, self.customer_mobile,
                            self.customer_email]
        fare_details = json.loads(self.fare_details)
        if 'taxes' not in fare_details:
            fare_details['taxes'] = {
                'sgst': 0,
                'cgst': 0
            }
        booking_items = [{
            'description': (
                '<b>From</b>: {source}   <b>Drop</b>: {destination}<br />\n'
                '<b>Travel date & time</b>: {travel_date} {travel_time}<br />\n'
                '<b>Vehicle type</b>: {vehicle_type}, <b>Booking type</b>: {booking_type}'
            ).format(
                source=self.source,
                destination=self.destination,
                travel_date=self.travel_date.strftime('%d %b %Y'),
                travel_time=self.travel_time.strftime('%I:%M %p'),
                vehicle_type=self.vehicle_type,
                booking_type=BOOKING_TYPE_CHOICES_DICT.get(self.booking_type)
            ),
            'amount': fare_details['price']
        }]
        total_amount = fare_details.get('total') or fare_details.get('price')
        f = open('/tmp/oc-booking-invoice-{}.pdf'.format(self.booking_id),
                 'wb')
        draw_pdf(f, {'id': self.booking_id,
                     'date': self.last_payment_date or self.created,
                     'customer_details': customer_details,
                     'items': booking_items,
                     'sgst': fare_details['taxes']['SGST'],
                     'cgst': fare_details['taxes']['CGST'],
                     'total_amount': total_amount,
                     'business_name': settings.INVOICE_BUSINESS_NAME,
                     'address': settings.INVOICE_BUSINESS_ADDRESS,
                     'footer': settings.INVOICE_FOOTER
                    })
        f.close()
        return f.name
