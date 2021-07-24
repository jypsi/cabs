from datetime import datetime

from django.contrib import admin
from django.utils import timezone
from django.utils.safestring import mark_safe
from import_export import resources
from import_export.admin import ExportMixin
from import_export import fields

from djangoql.admin import DjangoQLSearchMixin

from .models import Payment


class PaymentResource(resources.ModelResource):
    booking_id = fields.Field()
    customer_name = fields.Field()
    travel_datetime = fields.Field()

    class Meta:
        model = Payment
        fields = ['invoice_id', 'booking_id', 'customer_name',
                  'travel_datetime', 'mode', 'status', 'amount',
                  'reference_id', 'comment', 'accounts_verified',
                  'accounts_received', 'accounts_due', 'accounts_comment',
                  'created_by', 'created', 'accounts_last_updated_by',
                  'accounts_last_updated']
        export_order = fields

    def dehydrate_booking_id(self, payment):
        return payment.bookings.first().booking_id

    def dehydrate_customer_name(self, payment):
        return payment.bookings.first().customer_name

    def dehydrate_travel_datetime(self, payment):
        booking = payment.bookings.first()
        return datetime.combine(booking.travel_date, booking.travel_time)

    def dehydrate_amount(self, payment):
        return payment.amount.amount



@admin.register(Payment)
class PaymentAdmin(ExportMixin, DjangoQLSearchMixin, admin.ModelAdmin):
    list_filter = ('type', 'accounts_verified', 'created_by', 'created', 'mode',
                   'accounts_last_updated_by', 'accounts_last_updated')
    search_fields = ('bookings__booking_id',
                     'bookings__customer_name', 'bookings__travel_date')

    resource_class = PaymentResource


    def booking(self, obj):
        return mark_safe(
            '<a href="{}">{}</a>'.format(obj.item_object.get_admin_url(),
                                         obj.item_object)
        )

    def travel_datetime(self, obj):
        return datetime.combine(obj.item_object.travel_date, obj.item_object.travel_time)

    def customer_name(self, obj):
        return obj.item_object.customer_name

    def save_model(self, request, obj, form, change):
        if not obj.id or obj.created_by is None:
            obj.created_by = request.user
        obj.last_updated_by = request.user
        if request.user.has_perm('finance.verify_payment'):
            obj.accounts_last_updated_by = request.user
            obj.accounts_last_updated = timezone.now()

        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        fields = ['created_by', 'last_updated_by', 'created', 'last_updated',
                  'accounts_last_updated', 'accounts_last_updated_by']
        if not request.user.has_perm('finance.verify_payment'):
            fields.extend(['accounts_verified', 'accounts_received', 'accounts_due', 'accounts_comment'])
        return fields

    def get_list_display(self, request):
        fields = ['invoice_id', 'booking', 'customer_name', 'travel_datetime', 'mode', 'status', 'amount', 'reference_id', 'comment']
        if request.user.has_perm('finance.verify_payment'):
            fields.extend(['accounts_verified', 'accounts_received', 'accounts_due', 'accounts_comment',])
            self.list_editable = ['accounts_verified', 'accounts_received', 'accounts_comment']
        fields.extend(['created_by', 'created', 'accounts_last_updated_by', 'accounts_last_updated'])
        return fields

    booking.allow_tags = True
