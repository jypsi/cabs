import os
from opencabs.default_settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASS', 'postgres'),
        'HOST': 'db',
        'PORT': 5432
    }
}

INVOICE_BUSINESS_NAME = os.environ.get('INVOICE_BUSINESS_NAME', 'Gauranga Travels')

INVOICE_BUSINESS_ADDRESS = """
Mayapur Community Development Trust
ISKCON, Mayapur, Near Gada Bhavan,
Nadia, West Bengal
9593959990, 9593479990, 03472-245728
www.gaurangatravels.in
travels.mayapur@gmail.com

GSTIN: 19AADTM9050B1ZN
"""

INVOICE_FOOTER = """
NOTES:
1. Please pay the vehicle fare before using the car.
2. Parking & toll fee to be paid directly to the driver.
3. Per hour waiting charges of Rs. 50 for a small car, or Rs. 100 for a large car are
    applicable.
4. Booking charge of Rs. 300 is non refundable.
"""
