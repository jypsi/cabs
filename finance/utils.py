from django.conf import settings

from utils import import_path


def get_provider():
    path = settings.PAYMENT_PROVIDERS[settings.PAYMENT_PROVIDER]['CLASS']
    return import_path(path)(settings.PAYMENT_PROVIDERS[settings.PAYMENT_PROVIDER])
