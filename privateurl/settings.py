"""
(C) 2013-2024 Copycat Software, LLC. All Rights Reserved.
"""

from django.conf import settings


PRIVATEURL_URL_NAMESPACE = getattr(settings, "PRIVATEURL_URL_NAMESPACE", "privateurl")
PRIVATEURL_DEFAULT_TOKEN_SIZE = getattr(settings, "PRIVATEURL_DEFAULT_TOKEN_SIZE", 16)
