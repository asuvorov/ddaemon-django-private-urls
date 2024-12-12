"""
(C) 2013-2024 Copycat Software, LLC. All Rights Reserved.
"""

import datetime

from django.contrib.auth import get_user_model

from django.urls import reverse, NoReverseMatch
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import resolve_url
from django.test import TestCase
from django.utils.encoding import force_str

from privateurl.models import PrivateUrl
from privateurl.signals import privateurl_ok, privateurl_fail


class TestPrivateUrl(TestCase):
    def test_manager_create(self):
        """Docstring."""
        t = PrivateUrl.create("test", expire=datetime.timedelta(days=5))
        self.assertIsInstance(t, PrivateUrl)
        self.assertIsNotNone(t.pk)
        token_min_size_bak = PrivateUrl.TOKEN_MIN_SIZE
        try:
            PrivateUrl.TOKEN_MIN_SIZE = 1
            with self.assertRaises(RuntimeError):
                for i in range(100):
                    PrivateUrl.create("test", token_size=1)
        finally:
            PrivateUrl.TOKEN_MIN_SIZE = token_min_size_bak
        with self.assertRaises(AttributeError):
            PrivateUrl.create("test", token_size="test")
        with self.assertRaises(AttributeError):
            PrivateUrl.create("test", token_size=[10, 20, 30])

    def test_manager_create_with_replace(self):
        """Docstring."""
        PrivateUrl.create(
            action="test",
            replace=True)
        PrivateUrl.create(
            action="test",
            replace=True)
        self.assertEqual(PrivateUrl.objects.filter(action="test").count(), 2)

        # ---------------------------------------------------------------------
        user = get_user_model().objects.create(
            username="test",
            email="test@mail.com",
            password="test")
        PrivateUrl.create(
            action="test",
            user=user,
            replace=True)
        PrivateUrl.create(
            action="test",
            user=user,
            replace=True)
        self.assertEqual(PrivateUrl.objects.filter(action="test", user=user).count(), 1)

    def test_token_size(self):
        """Docstring."""
        t = PrivateUrl.create("test", token_size=50)
        self.assertEqual(len(t.token), 50)

        for i in range(100):
            t = PrivateUrl.create("test", token_size=16)
            self.assertTrue(len(t.token) == 16)

        self.assertRaises(AttributeError, PrivateUrl.create, "test", token_size=0)
        self.assertRaises(AttributeError, PrivateUrl.create, "test", token_size=-1)
        self.assertRaises(AttributeError, PrivateUrl.create, "test", token_size=(0, 0))
        self.assertRaises(AttributeError, PrivateUrl.create, "test", token_size=(36, 65))
        self.assertRaises(AttributeError, PrivateUrl.create, "test", token_size=(60, 36))
        self.assertRaises(AttributeError, PrivateUrl.create, "test", token_size=(-1, 36))
        self.assertRaises(AttributeError, PrivateUrl.create, "test", token_size=(-2, -1))

    def test_data(self):
        """Docstring."""
        d = {
            "k":    ["v"],
        }
        t = PrivateUrl.create("test", data=d)
        self.assertIsNot(t.data, d)
        self.assertIsNot(t.data["k"], d["k"])

    def test_manager_get_object_or_None(self):
        """Docstring."""
        t = PrivateUrl.create("test")
        j = PrivateUrl.objects.get_object_or_None(t.action, t.token)
        self.assertIsInstance(j, PrivateUrl)
        self.assertEqual(t.pk, j.pk)

        n = PrivateUrl.objects.get_object_or_None("none", "none")
        self.assertIsNone(n)

    def test_get_absolute_url(self):
        """Docstring."""
        t = PrivateUrl.create("test")
        url = reverse("purl:privateurl", kwargs={
            "action":   t.action,
            "token":    t.token,
        })
        self.assertEqual(t.get_absolute_url(), url)
        self.assertEqual(resolve_url(t), url)

    def test_is_available(self):
        """Docstring."""
        t = PrivateUrl.create("test")
        self.assertTrue(t.is_available())
        t.hits_limit = 1
        t.hit_counter = 1
        self.assertFalse(t.is_available())
        t.hits_limit = 0
        self.assertTrue(t.is_available())
        t.expire = datetime.datetime(2015, 10, 10, 10, 10, 10)
        self.assertTrue(t.is_available(dt=datetime.datetime(2015, 10, 10, 10, 10, 9)))
        self.assertFalse(t.is_available(dt=datetime.datetime(2015, 10, 10, 10, 10, 11)))

    def test_hit_counter_inc(self):
        """Docstring."""
        t = PrivateUrl.create("test")
        t.hit_counter_inc()
        self.assertEqual(t.hit_counter, 1)
        self.assertIsNotNone(t.first_hit)
        self.assertIsNotNone(t.last_hit)
        self.assertEqual(t.first_hit, t.last_hit)
        self.assertIsNotNone(t.pk)
        t.hit_counter_inc()
        self.assertEqual(t.hit_counter, 2)
        j = PrivateUrl.create("test", auto_delete=True)
        j.hit_counter_inc()
        self.assertIsNone(j.pk)

    def test_long_action_name_fail(self):
        """Docstring."""
        action = "a" * 32
        a = PrivateUrl.create(action)
        b = PrivateUrl.objects.get(action=action)
        self.assertEqual(a, b)
        self.assertEqual(len(b.action), len(action))

    def test_reverse(self):
        """Docstring."""
        a = PrivateUrl.create("a" * 32)
        try:
            a.get_absolute_url()
        except NoReverseMatch as e:
            raise self.failureException("Private url reverse url error ({}).".format(e))

    def test_generate_token(self):
        """Docstring."""
        self.assertEqual(len(PrivateUrl.generate_token(size=(60, 60))), 60)
        self.assertEqual(len(PrivateUrl.generate_token(size=(60, 60))), 59)  # strip end dash


class TestPrivateUrlView(TestCase):
    @classmethod
    def setUpClass(cls):
        """Docstring."""
        super(TestPrivateUrlView, cls).setUpClass()

        @receiver(privateurl_ok, weak=False, dispatch_uid="ok")
        def ok(action, **kwargs):  # noqa: F841
            """Docstring."""
            if action == "test":
                return {
                    "response": HttpResponse("ok"),
                }

        @receiver(privateurl_fail, weak=False, dispatch_uid="fail")
        def fail(action, **kwargs):  # noqa: F841
            """Docstring."""
            if action == "test":
                return {
                    "response": HttpResponse("fail"),
                }

    @classmethod
    def tearDownClass(cls):
        """Docstring."""
        super(TestPrivateUrlView, cls).tearDownClass()
        privateurl_ok.disconnect(dispatch_uid="ok")
        privateurl_fail.disconnect(dispatch_uid="fail")

    def test_receivers(self):
        """Docstring."""
        t = PrivateUrl.create("test")
        response = self.client.get(t.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content), "ok")
        response = self.client.get(t.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content), "fail")
        t.action = "none"
        response = self.client.get(t.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_receivers2(self):
        """Docstring."""
        t = PrivateUrl.create("test2")
        response = self.client.get(t.get_absolute_url())
        self.assertEqual(response.status_code, 302)
        response = self.client.get(t.get_absolute_url())
        self.assertEqual(response.status_code, 404)


class TestPrivateUrlAdmin(TestCase):
    @classmethod
    def setUpClass(cls):
        """Docstring."""
        super(TestPrivateUrlAdmin, cls).setUpClass()
        PrivateUrl.create("test")
        get_user_model().objects.create_superuser("admin", "admin@site.com", "admin")

    def setUp(self):
        """Docstring."""
        self.client.login(username="admin", password="admin")

    def tearDown(self):
        """Docstring."""
        self.client.logout()

    def test_admin_list(self):
        """Docstring."""
        response = self.client.get(resolve_url("admin:privateurl_privateurl_changelist"))
        self.assertEqual(response.status_code, 200)
