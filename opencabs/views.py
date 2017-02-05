from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.urls import reverse

from formtools.wizard.views import CookieWizardView

from .forms import booking as booking_form
from .models import Booking

FORMS = [
    ('itinerary', booking_form.BookingTravelForm),
    ('vehicles', booking_form.BookingVehiclesForm),
    ('contactinfo', booking_form.BookingContactInfoForm)
]

TEMPLATES = {
    'itinerary': 'opencabs/index.html',
    'vehicles': 'opencabs/booking_vehicles.html',
    'contactinfo': 'opencabs/booking_contactinfo.html'
}


class BookingWizard(CookieWizardView):

    form_list = FORMS

    def get_context_data(self, form, **kwargs):
        context_data = super().get_context_data(form, **kwargs)
        context_data['settings'] = settings
        return context_data

    def get_form_kwargs(self, step):
        data = {}
        if step == 'vehicles':
            itinerary_data = self.get_cleaned_data_for_step('itinerary')
            data.update({'source': itinerary_data['source'],
                         'destination': itinerary_data['destination'],
                         'booking_type': itinerary_data['booking_type']})
        return data

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, form_dict, **kwargs):
        data = form_dict['itinerary'].cleaned_data
        data.update(form_dict['vehicles'].cleaned_data)
        data.update(form_dict['contactinfo'].cleaned_data)
        booking = Booking(**data)
        booking.save()
        return redirect(reverse('booking_details', args=[booking.pnr]))

booking_wizard = BookingWizard.as_view()


def index(request):
    return render(request, 'opencabs/index.html', {
        'settings': settings,
        'wizard': booking_wizard
    })


def booking_details(request):
    pnr = request.GET.get('pnr', '').upper()
    booking = get_object_or_404(Booking, pnr=pnr)
    return render(request, 'opencabs/booking_details.html', {
        'settings': settings,
        'booking': booking
    })
