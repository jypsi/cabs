from django.conf.urls import url

from .views import start, success, cancel, index

urlpatterns = [
    url(r'^success/$', success),
    url('^start/$', start, name='payment_start'),
    url('^cancel/$', cancel),
    url('^index/$', index, name='payment_index')
]
