from django import forms
from django.conf import settings
from django.template.loader import render_to_string

from ..models import Booking, Rate


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
            'travel_date', 'travel_time')


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
        fields = ('customer_name', 'customer_mobile', 'pickup_point', 'ssr')
