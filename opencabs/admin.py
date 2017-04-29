from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django import forms
from django.contrib.contenttypes.admin import GenericTabularInline

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from finance.models import Payment
from .models import (Booking, Place, Rate, VehicleCategory, VehicleFeature,
                     Vehicle, Driver, VehicleRateCategory)
from .notification import send_sms


class BookingResource(resources.ModelResource):

    class Meta:
        model = Booking


class PaymentInline(GenericTabularInline):
    model = Payment
    extra = 1
    ct_field = 'item_content_type'
    ct_fk_field = 'item_object_id'
    readonly_fields = ('invoice_id', )
    can_delete = False


@admin.register(Booking)
class BookingAdmin(ImportExportModelAdmin):
    list_display = ('booking_id', 'customer_name', 'customer_mobile',
                    'source', 'destination', 'booking_type',
                    'travel_date', 'travel_time', 'vehicle', 'status',
                    'total_fare', 'payment_done', 'payment_status',
                    'payment_due', 'paid_to_driver')
    list_filter = ('booking_type', 'vehicle', 'status', 'travel_date')
    search_fields = ('booking_id', 'customer_name', 'customer_mobile',
                     'travel_date')
    readonly_fields = ('total_fare', 'payment_due', 'payment_done',
                       'payment_status', 'fare_details')
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
                    ('total_fare', 'payment_done', 'payment_due'),
                    ('payment_status', 'fare_details'),
                    ('paid_to_driver', 'driver_invoice_id')
                )
            }
        )
    )
    resource_class = BookingResource

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj:
            if obj.paid_to_driver:
                readonly_fields += ('paid_to_driver', 'driver_invoice_id')
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
