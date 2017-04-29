from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.conf import settings

import uuid
from hashlib import md5

from djmoney.models.fields import MoneyField


PAYMENT_MODE_CHOICES = (
    ('CA', 'Cash'),
    ('BT', 'Bank Transfer')
)

PAYMENT_TYPE_CHOICES = (
    (1, 'Income'),
    (-1, 'Expenditure')
)


class Payment(models.Model):
    amount = MoneyField(
         max_digits=10, decimal_places=2, default_currency='INR')
    type = models.IntegerField(choices=PAYMENT_TYPE_CHOICES, default=1,
                               blank=True)
    mode = models.CharField(choices=PAYMENT_MODE_CHOICES, max_length=50,
                            default='CA')
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True)

    # auto generated
    timestamp = models.DateTimeField(blank=True, default=timezone.now)
    invoice_id = models.CharField(max_length=50, blank=True)

    # Item towards which this payment is made
    item_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE)
    item_object_id = models.PositiveIntegerField()
    item_object = GenericForeignKey('item_content_type', 'item_object_id')

    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return '%s' % self.received

    @property
    def received(self):
        return self.type * self.amount

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = self._create_invoice_id()
        super().save(*args, **kwargs)

    def _create_invoice_id(self):
        text = str(uuid.uuid1())
        return (settings.INVOICE_ID_PREFIX + md5(
            text.encode('utf-8')).hexdigest()[:8]).upper()
