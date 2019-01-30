from django.conf.urls import url

from .views import start, success, cancel

urlpatterns = [
    url(r'^payment/success/$'), success,
    url('^payment/start/$'), start,
    url('^payment/cancel/$'), cancel,
]
