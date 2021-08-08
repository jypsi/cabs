from django import forms
from django.conf import settings
from django.template.loader import render_to_string

from ..models import Booking, Rate, BOOKING_PAYMENT_METHOD_CHOICES_DICT


class BaseBookingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class BookingTravelForm(BaseBookingForm):
    class Meta:
        model = Booking
        fields = (
            'source', 'destination', 'booking_type',
            'travel_date', 'travel_time', 'passengers')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['booking_type'].widget = forms.RadioSelect()
        self.fields['booking_type'].widget.choices = self.fields['booking_type'].choices[1:]
        self.fields['booking_type'].widget.attrs = {'class': 'radio-inline'}
        self.fields['source'].queryset = self.fields['source'].queryset.order_by('name')
        self.fields['destination'].queryset = self.fields['destination'].queryset.order_by('name')



class BookingVehiclesForm(BaseBookingForm):
    class Meta:
        model = Booking
        fields = ('vehicle_type',)

    def __init__(self, *args, **kwargs):
        source = kwargs.pop('source')
        destination = kwargs.pop('destination')
        booking_type = kwargs.pop('booking_type')
        super().__init__(*args, **kwargs)
        self.fields['vehicle_type'].widget = forms.RadioSelect()
        code = settings.ROUTE_CODE_FUNC(source.name, destination.name)
        choices = []
        for rate in Rate.objects.filter(code=code):
            label = render_to_string(
                'opencabs/partials/vehicle_rate_label.html',
                context={'rate': rate, 'booking_type': booking_type})
            choices.append((rate.vehicle_category_id, label))
        self.fields['vehicle_type'].choices = choices
        self.fields['vehicle_type'].widget.attrs = {'hidden': 'true'}


class BookingContactInfoForm(BaseBookingForm):
    class Meta:
        model = Booking
        fields = ('customer_name', 'customer_mobile', 'customer_email',
                  'pickup_point', 'ssr')
        widgets = {
            'pickup_point': forms.Textarea(attrs={'rows': 3}),
            'ssr': forms.Textarea(attrs={'rows': 3})
        }

    def clean(self):
        cleaned_data = super().clean()
        customer_mobile = cleaned_data.get('customer_mobile')
        customer_email = cleaned_data.get('customer_email')

        if not customer_mobile and not customer_email:
            raise forms.ValidationError(
                'One of mobile and email is required.')


class BookingPaymentInfoForm(BaseBookingForm):
    class Meta:
        model = Booking
        fields = ('payment_method',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].choices = tuple([
            (item, BOOKING_PAYMENT_METHOD_CHOICES_DICT.get(item)) for item in settings.BOOKING_FORM_PAYMENT_MODES
            if BOOKING_PAYMENT_METHOD_CHOICES_DICT.get(item)
        ])
