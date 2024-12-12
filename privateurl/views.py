"""
(C) 2013-2024 Copycat Software, LLC. All Rights Reserved.
"""

import logging

from termcolor import cprint

from django.http.response import (
    Http404,
    HttpResponseRedirect)

from ddcore.Decorators import log_default

from privateurl.models import PrivateUrl
from privateurl.signals import (
    privateurl_ok,
    privateurl_fail)


logger = logging.getLogger(__name__)


@log_default(my_logger=logger, cls_or_self=False)
def privateurl_view(request, action, token):
    """Docstring."""
    obj = PrivateUrl.objects.get_object_or_None(action, token)
    ok = False

    if (
            not obj or
            not obj.is_available()):
        results = privateurl_fail.send(
            sender=PrivateUrl,
            request=request,
            obj=obj,
            action=action)
    else:
        results = privateurl_ok.send(
            sender=PrivateUrl,
            request=request,
            obj=obj,
            action=action)
        obj.hit_counter_inc()
        ok = True

    # cprint(f"    [--- INFO ---] RESULTS  : {results}\n"
    #        f"                   OBJ      : {obj}\n"
    #        f"                   OK       : {ok}", "cyan")

    for receiver, result in results:
        if isinstance(result, dict):
            if "response" in result:
                return result["response"]

    if not ok:
        raise Http404

    return HttpResponseRedirect("/")
