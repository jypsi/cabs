from django.contrib import admin

from .models import Booking, Place, Rate, VehicleCategory, VehicleFeature

admin.site.register(Booking)
admin.site.register(Place)
admin.site.register(Rate)
admin.site.register(VehicleCategory)
admin.site.register(VehicleFeature)
