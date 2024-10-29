import django

from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("private/", include(("privateurl.urls", "privateurl"), namespace="purl")),
]
