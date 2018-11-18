from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('item_object', 'created_by', 'amount', 'customer', 'type', 'mode', 'timestamp',
                    'travel_date', 'reference_id', 'comment',  'created',)
    list_filter = ('mode', 'timestamp', 'created_by')
    search_fields = ('bookings__booking_id', 'created_by__username', 'timestamp')
    readonly_fields = ('created_by',)

    def item_object(self, obj):
        return '<a href="{}">{}</a>'.format(obj.item_object.get_admin_url(),
                                            obj.item_object)

    def customer(self, obj):
        return obj.item_object.customer_name

    def travel_date(self, obj):
        return obj.item_object.travel_date

    item_object.allow_tags = True

    def save_model(self, request, obj, form, change):
        if not obj.id or obj.user is None:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
