"""
(C) 2013-2024 Copycat Software, LLC. All Rights Reserved.
"""

import datetime
import random

from django.conf import settings

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse  # noqa

from django.core.validators import RegexValidator
from django.db import models, IntegrityError
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from ddcore.Decorators import autoconnect
from ddcore.models import BaseModel
from ddcore.Serializers import JSONEncoder

from . import settings as purl_settings


class PrivateUrlManager(models.Manager):
    """Private URL Manager."""

    def get_object_or_None(self, action, token):
        "Docstring."
        try:
            return self.select_related("user").get(
                action=action,
                token=token)
        except self.model.DoesNotExist:
            pass


@autoconnect
class PrivateUrl(BaseModel):
    """Private URL Model."""

    TOKEN_MIN_SIZE = 8
    TOKEN_MAX_SIZE = 64

    # -------------------------------------------------------------------------
    # --- Basics.
    # -------------------------------------------------------------------------
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_index=True,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="shared_private_urls",
        verbose_name=_("User"),
        help_text=_("User"))

    action = models.SlugField(
        max_length=255,
        db_index=True,
        validators=[RegexValidator(r"^[-_a-zA-Z0-9]+$")],
        verbose_name=_("Action"),
        help_text=_("Action"))
    token = models.SlugField(
        max_length=TOKEN_MAX_SIZE,
        validators=[RegexValidator(r"^[-a-zA-Z0-9]+$")],
        verbose_name=_("Token"),
        help_text=_("Token"))

    data = models.JSONField(
        null=True, blank=True,
        encoder=JSONEncoder,
        verbose_name=_("Data"),
        help_text=_("Data"))

    hits_limit = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Hits Limit"),
        help_text=_("Set 0 to unlimited."))
    hit_counter = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Hits Counter"))

    # -------------------------------------------------------------------------
    # --- Significant Dates.
    # -------------------------------------------------------------------------
    first_hit = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("First Hit"),
        help_text=_("Date of the first Hit."))
    last_hit = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("Last Hit"),
        help_text=_("Date of the last Hit."))
    expire = models.DateTimeField(
        db_index=True,
        null=True, blank=True,
        verbose_name=_("Expiration Date"),
        help_text=_("Expiration Date."))

    # -------------------------------------------------------------------------
    # --- Flags.
    # -------------------------------------------------------------------------
    auto_delete = models.BooleanField(
        default=False,
        verbose_name=_("Auto-delete?"),
        help_text=_("Delete Object, if it can no longer be used?"))

    objects = PrivateUrlManager()

    class Meta:
        # db_table = "privateurl_privateurl"
        ordering = ("-created",)
        unique_together = ("action", "token")
        verbose_name = _("private url")
        verbose_name_plural = _("private urls")

    @classmethod
    def create(
            cls, action, user=None, data=None, hits_limit=1, expire=None,
            auto_delete=False, token_size=None, replace=False):
        """Create a new PrivateUrl Object.

        Parameters
        ----------
        action              :str        Action Name.
        user                :obj        User Object or `None`.
        data                :dict       Additional Data.
        hits_limit          :int        Limit the Request Hits (0 for unlimited Hits).
        expire              :datetime   Expiration Time, Date/Time, Time-delta (`None` to disable
                                        the Time Limit).
        auto_delete         :bool       Automatically remove, when URL is not available.
        token_size          :int        Length of Token (`None` for default Value from Settings).
        replace             :bool       Remove existing Object for User and Action before creating
                                        a new one.

        Returns
        -------
                            :obj        Private URL Object.

        Raises
        ------
        IntegrityError

        """
        if (
                replace and
                user):
            cls.objects.filter(action=action, user=user).delete()

        if isinstance(expire, datetime.timedelta):
            expire = timezone.now() + expire

        try:
            token = cls.generate_token(token_size=token_size)
            obj = PrivateUrl(
                user=user,
                action=action,
                token=token,
                data=data,
                hits_limit=hits_limit,
                expire=expire,
                auto_delete=auto_delete)

            with transaction.atomic():
                obj.save()

            return obj

        except IntegrityError:
            raise RuntimeError(f"Failed to create `PrivateUrl` Object ({action=}, {token_size=})")

        except Exception as exc:
            raise exc

    def is_available(self, dt=None):
        """ Return True, if the Object can be used."""
        if (
                self.expire and
                self.expire <= (dt or timezone.now())):
            return False

        if (
                self.hits_limit and
                self.hits_limit <= self.hit_counter):
            return False

        return True

    def hit_counter_inc(self):
        """Increment Hits Counter."""
        obj_is_exists = self.pk is not None
        now = timezone.now()

        self.hit_counter += 1

        if (
                self.auto_delete and
                not self.is_available(dt=now)):
            if obj_is_exists:
                self.delete()

            return

        uf = {"hit_counter", "last_hit"}

        if not self.first_hit:
            self.first_hit = now
            uf.add("first_hit")

        self.last_hit = now

        if obj_is_exists:
            self.save(update_fields=uf)

    @classmethod
    def generate_token(cls, token_size=None):
        """Generate new unique Token.

        Parameters
        ----------
        token_size          :int        Length of Token (`None` for default Value from Settings).

        Returns
        -------
        Response            :obj        Service Status.

        Raises
        ------
        AttributeError

        """
        if token_size is None:
            token_size = purl_settings.PRIVATEURL_DEFAULT_TOKEN_SIZE

        if not isinstance(token_size, int):
            raise AttributeError("Attribute `token_size` must be `int`.")

        if (
                token_size < cls.TOKEN_MIN_SIZE or
                token_size > cls.TOKEN_MAX_SIZE):
            raise AttributeError(
                f"Attribute `token_size` Value must be between {cls.TOKEN_MIN_SIZE} and "
                f"{cls.TOKEN_MAX_SIZE}.")

        return get_random_string(length=token_size)

    def get_absolute_url(self):
        """Get absolute URL."""
        return reverse(
            "{}:privateurl".format(purl_settings.PRIVATEURL_URL_NAMESPACE), kwargs={
                "action":   self.action,
                "token":    self.token,
            })
