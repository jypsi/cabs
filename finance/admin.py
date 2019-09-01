from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_filter = ('created_by', 'mode', 'created_by', 'accounts_verified')
    search_fields = ('created', 'timestamp')

    def save_model(self, request, obj, form, change):
        if not obj.id or obj.created_by is None:
            obj.created_by = request.user
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        fields = ['created_by', 'last_updated_by', 'created', 'last_updated']
        if not request.user.has_perm('finance.verify_payment'):
            fields.extend(['accounts_verified', 'accounts_received', 'accounts_due', 'accounts_comment'])
        return fields

    def get_list_display(self, request):
        fields = ['invoice_id', 'mode', 'status', 'created_by', 'created', 'amount', 'comment']
        if request.user.has_perm('finance.verify_payment'):
            fields.extend(['accounts_verified', 'accounts_received', 'accounts_comment', 'accounts_due'])
            self.list_editable = ['accounts_verified', 'accounts_received', 'accounts_comment']
        return fields
