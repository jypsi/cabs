"""opencabs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from django.contrib.flatpages import views as flatpages_views
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^' + settings.URL_PREFIX + r'$', views.booking_wizard, name='index'),
    url(r'^' + settings.URL_PREFIX + r'booking/$', views.booking_details,
        name='booking_details'),
    url(r'^' + settings.URL_PREFIX + 'booking/(?P<booking_id>\d+)/invoice/$',
        views.booking_invoice, name='booking_invoice'),
    url(r'^' + settings.URL_PREFIX + r'payment/', include('finance.urls')),
    url(r'^' + settings.URL_PREFIX + r'admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    url(r'^' + settings.URL_PREFIX + r'(?P<url>.*/)$', flatpages_views.flatpage),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
