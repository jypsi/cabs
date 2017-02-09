from django.contrib import admin

from .models import (Booking, Place, Rate, VehicleCategory, VehicleFeature,
                     Vehicle, Driver, VehicleRateCategory)
from .notification import send_sms


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer_name', 'customer_mobile',
                    'source', 'destination', 'booking_type',
                    'travel_datetime', 'vehicle', 'status')
    list_filter = ('booking_type', 'vehicle', 'status')
    search_fields = ('booking_id', 'customer_name', 'customer_mobile')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        status = form.cleaned_data['status']
        if 'status' in form.changed_data:
            if status == '1':
                msg = (
                    "Your booking with ID: {} has been confirmed.\n"
                    "You'll be notified about vehicle & driver details "
                    "a few hours before your trip."
                ).format(obj.booking_id)
            elif status == '2':
                msg = (
                    "Your booking with ID: {} has been declined."
                ).format(obj.booking_id)
            send_sms([form.cleaned_data['customer_mobile']], msg)


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
