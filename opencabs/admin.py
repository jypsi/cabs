from django.contrib import admin

from .models import Booking, Place, Rate, VehicleCategory, VehicleFeature


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('pnr', 'customer_name', 'customer_mobile',
                    'source', 'destination', 'booking_type',
                    'travel_datetime', 'vehicle', 'status')
    list_filter = ('booking_type', 'vehicle', 'status')
    search_fields = ('pnr', 'customer_name', 'customer_mobile')


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('source', 'destination', 'vehicle_category',
                    'oneway_price', 'driver_charge')
    list_filter = ('vehicle_category',)


@admin.register(VehicleCategory)
class VehicleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'tariff_per_km', 'tariff_after_hours')
    list_filter = ('features',)

admin.site.register(VehicleFeature)
