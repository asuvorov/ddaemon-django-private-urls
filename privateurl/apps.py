"""
(C) 2013-2024 Copycat Software, LLC. All Rights Reserved.
"""

from importlib import import_module

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PrivateURLConfig(AppConfig):
    """Docstring."""

    name = "privateurl"
    verbose_name = _("Django Private URL")

    def ready(self):
        """Docstring."""
        import_module("privateurl.tasks")
