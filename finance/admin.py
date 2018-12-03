from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_filter = ('mode', 'timestamp', 'created_by',)
    search_fields = ('bookings__booking_id', 'created_by__username', 'timestamp')
    list_editable = []

    def item_object(self, obj):
        return '<a href="{}">{}</a>'.format(obj.item_object.get_admin_url(),
                                            obj.item_object)

    def customer(self, obj):
        return obj.item_object.customer_name

    def travel_date(self, obj):
        return obj.item_object.travel_date

    item_object.allow_tags = True

    def save_model(self, request, obj, form, change):
        if not obj.id or obj.created_by is None:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        fields = ['created_by',]
        if not request.user.has_perm('finance.verify_payment'):
            fields.extend(['accounts_verified', 'accounts_verified_timestamp'])
        return fields

    def get_list_display(self, request):
        fields = ['item_object', 'created_by', 'amount']
        if request.user.has_perm('finance.verify_payment'):
            fields.extend(['accounts_verified', 'accounts_verified_timestamp'])
            self.list_editable = ['accounts_verified', 'accounts_verified_timestamp']
        fields.extend(['customer', 'type', 'mode', 'timestamp', 'travel_date', 'reference_id', 'comment',  'created'])
        return fields
