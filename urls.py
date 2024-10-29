"""(C) 2013-2024 Copycat Software, LLC. All Rights Reserved."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import (
    include,
    re_path)


admin.autodiscover()


urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
