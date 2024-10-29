"""
(C) 2013-2024 Copycat Software, LLC. All Rights Reserved.
"""

from django.urls import re_path

from . import views


urlpatterns = [
    re_path(r"^(?P<action>[\-_a-zA-Z0-9]{1,255})/(?P<token>[\-a-zA-Z0-9]{1,64})$",
        views.privateurl_view,
        name="privateurl"),

    path("admin/", admin.site.urls),
    path("private", namespace="purl"),
]
