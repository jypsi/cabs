from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OpencabsConfig(AppConfig):
    name = 'opencabs'
    verbose_name = _('opencabs')

    def ready(self):
        import opencabs.signals  # noqa
