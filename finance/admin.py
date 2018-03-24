from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('amount', 'type', 'mode', 'timestamp',
                    'item_object', 'reference_id', 'comment', 'created')
    list_filter = ('mode', 'created')
