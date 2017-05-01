from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django import forms
from django.contrib.contenttypes.admin import GenericTabularInline

from import_export import resources
from import_export.admin import ExportMixin
from import_export import fields

from finance.models import Payment
from .models import (Booking, Place, Rate, VehicleCategory, VehicleFeature,
                     Vehicle, Driver, VehicleRateCategory)
from .models import (BOOKING_TYPE_CHOICES_DICT,
                     BOOKING_STATUS_CHOICES_DICT,
                     BOOKING_PAYMENT_STATUS_CHOICES_DICT)
from .notification import send_sms


class BookingResource(resources.ModelResource):
    booking_type = fields.Field()
    source = fields.Field()
    destination = fields.Field()
    driver = fields.Field()
    driver_paid = fields.Field()
    vehicle_type = fields.Field()
    status = fields.Field()
    payment_status = fields.Field()

    class Meta:
        model = Booking
        exclude = ('accounts_verified',)
        export_order = ('id', 'booking_id', 'source', 'destination',
                        'booking_type', 'customer_name', 'customer_mobile',
                        'customer_email', 'created',
                        'travel_date', 'travel_time',
                        'pickup_point', 'ssr', 'status', 'vehicle_type',
                        'vehicle', 'driver', 'extra_info',
                        'total_fare',
                        'payment_status', 'payment_done', 'payment_due',
                        'driver_paid', 'driver_pay', 'driver_invoice_id',
                        'fare_details'
                        )

    def dehydrate_driver(self, booking):
        return str(booking.driver) if booking.driver else ''

    def dehydrate_source(self, booking):
        return booking.source.name

    def dehydrate_destination(self, booking):
        return booking.destination.name

    def dehydrate_vehicle_type(self, booking):
        return booking.vehicle_type.name

    def dehydrate_vehicle(self, booking):
        return str(booking.vehicle)

    def dehydrate_driver_paid(self, booking):
        return str(booking.driver_paid)

    def dehydrate_status(self, booking):
        return BOOKING_STATUS_CHOICES_DICT.get(booking.status)

    def dehydrate_payment_status(self, booking):
        return BOOKING_PAYMENT_STATUS_CHOICES_DICT.get(booking.payment_status)

    def dehydrate_booking_type(self, booking):
        return BOOKING_TYPE_CHOICES_DICT.get(booking.booking_type)


class PaymentInline(GenericTabularInline):
    model = Payment
    extra = 1
    ct_field = 'item_content_type'
    ct_fk_field = 'item_object_id'
    readonly_fields = ('invoice_id', )
    can_delete = False


@admin.register(Booking)
class BookingAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('booking_id', 'customer_name', 'customer_mobile',
                    'source', 'destination', 'booking_type',
                    'travel_date', 'travel_time', 'created', 'vehicle',
                    'status', 'total_fare', 'payment_done', 'payment_status',
                    'payment_due', 'driver_paid', 'driver_pay')
    list_filter = ('booking_type', 'vehicle', 'status', 'travel_date',
                   'created')
    search_fields = ('booking_id', 'customer_name', 'customer_mobile',
                     'travel_date')
    readonly_fields = ('total_fare', 'payment_due', 'payment_done',
                       'payment_status', 'fare_details', 'revenue',
                       'last_payment_date', 'driver_pay')
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 3, 'cols': 30})}
    }
    inlines = (PaymentInline,)
    fieldsets = (
        (
            'Customer details', {
                'fields': (
                    ('customer_name', 'customer_mobile', 'customer_email'),
                    ('pickup_point', 'ssr')
                ),
            }
        ),
        (
            'Travel details', {
                'fields': (
                    ('source', 'destination', 'travel_date', 'travel_time'),
                    ('booking_type', 'vehicle_type', 'vehicle', 'driver'),
                    ('status', 'extra_info', 'distance')
                )
            }
        ),
        (
            'Payment details', {
                'fields': (
                    ('total_fare', 'payment_done', 'payment_due', 'revenue'),
                    ('last_payment_date', 'payment_status', 'fare_details'),
                    ('driver_paid', 'driver_pay', 'driver_invoice_id')
                )
            }
        )
    )
    resource_class = BookingResource

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj:
            if obj.driver_paid:
                readonly_fields += ('driver_paid', 'driver_invoice_id')
        return readonly_fields

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        status = form.cleaned_data['status']
        if 'status' in form.changed_data:
            subject = ''
            if status == '1':
                msg = (
                    "Your booking with ID: {} has been confirmed.\n"
                    "You'll be notified about vehicle & driver details "
                    "a few hours before your trip."
                ).format(obj.booking_id)
                subject = 'Booking confirmed'
            elif status == '2':
                msg = (
                    "Your booking with ID: {} has been declined."
                ).format(obj.booking_id)
                subject = 'Booking declined'
            if form.cleaned_data.get('customer_mobile'):
                send_sms([form.cleaned_data['customer_mobile']], msg)
            if form.cleaned_data.get('customer_email'):
                send_mail(subject, msg,
                          settings.FROM_EMAIL,
                          [form.cleaned_data['customer_email']])

        if ('vehicle' in form.changed_data or
                'driver' in form.changed_data or
                'extra_info' in form.changed_data):
            msg = ("Trip details for booking ID: {}\n"
                   "Datetime: {} {}\n").format(
                       obj.booking_id,
                       obj.travel_date.strftime('%d %b, %Y'),
                       obj.travel_time.strftime('%I:%M %p')
                   )
            if obj.vehicle and obj.driver:
                msg += (
                    "Vehicle: {} ({})\n"
                    "Driver: {}, {}"
                ).format(obj.vehicle.name, obj.vehicle.number,
                         obj.driver.name, obj.driver.mobile)
            else:
                msg += obj.extra_info or ""
            if form.cleaned_data.get('customer_mobile'):
                send_sms([form.cleaned_data['customer_mobile']], msg)
            if form.cleaned_data.get('customer_email'):
                send_mail('Trip details',
                          msg, settings.FROM_EMAIL,
                          [form.cleaned_data['customer_email']])

        if 'driver' in form.changed_data:
            if obj.driver:
                msg = (
                    "Trip details for {booking_id}\n"
                    "{customer_name}, {customer_mobile}\n"
                    "on {travel_datetime}\n"
                    "from {source} to {destination}, "
                    "{booking_type_display}\n"
                    "Pickup: {pickup_point}"
                ).format(
                    booking_id=obj.booking_id,
                    customer_name=obj.customer_name,
                    customer_mobile=obj.customer_mobile,
                    travel_datetime='{} {}'.format(
                       obj.travel_date.strftime('%d %b, %Y'),
                       obj.travel_time.strftime('%I:%M %p')),
                    source=obj.source, destination=obj.destination,
                    booking_type_display=obj.booking_type_display,
                    pickup_point=obj.pickup_point
                )
                send_sms(obj.driver.mobile, msg)


class Account(Booking):
    class Meta:
        proxy = True


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'accounts_verified', 'payment_done',
                    'last_payment_date', 'revenue', 'driver_pay',
                    'driver_invoice_id')
    list_editable = ('accounts_verified',)
    fields = ('booking_id', 'accounts_verified', 'payment_done',
              'last_payment_date', 'revenue', 'driver_pay',
              'driver_invoice_id')
    readonly_fields = ('booking_id', 'payment_done',
                       'last_payment_date', 'revenue', 'driver_pay',
                       'driver_invoice_id')
    list_filter = ('accounts_verified',)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('source', 'destination', 'vehicle_category',
                    'oneway_price', 'roundtrip_price')
    list_filter = ('vehicle_category',)


@admin.register(VehicleRateCategory)
class VehicleRateCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'tariff_per_km', 'tariff_after_hours')
    list_filter = ('features',)


@admin.register(VehicleCategory)
class VehicleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile')
    search_fields = ('name', 'mobile')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'category', 'driver')
    search_fields = ('name', 'number', 'driver')
    list_filter = ('category__name',)

admin.site.register(VehicleFeature)
