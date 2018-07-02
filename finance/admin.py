from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('amount', 'type', 'mode', 'timestamp', 'customer',
                    'travel_date', 'item_object', 'reference_id',
                    'comment', 'created',)
    list_filter = ('mode', 'created')
    search_fields = ('bookings__booking_id',)

    def item_object(self, obj):
        return '<a href="{}">{}</a>'.format(obj.item_object.get_admin_url(),
                                            obj.item_object)

    def customer(self, obj):
        return obj.item_object.customer_name

    def travel_date(self, obj):
        return obj.item_object.travel_date


    item_object.allow_tags = True
