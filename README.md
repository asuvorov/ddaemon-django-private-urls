# ddaemon-django-private-url (Fork)

## Project Description

The Application helps easy and flexibly implement different Features, that require a Use of Private URL for Users, like Registration Confirmation, Password Recovery, Access to paid Content, and so on.

Low Level API provides a full Control and allows:

- limiting private url by time and hits

- auto removing urls that won't be used

- knowing number of hits, date of first and last hit for each url

- controlling token generator

- saving additional data in JSON format and using it at url hits

- processing succeeded or failed hits using django signals and controlling server responses

## Installation

**Requirements:**

* Django v1.8+
1. Install `django-privateurl`.
* Via pip::
  
  $ pip install django-privateurl

* Via setuptools::
  
  $ easy_install django-privateurl
  
  For install development version use `git+https://github.com/liminspace/django-privateurl.git@master`
  instead `django-privateurl`.
2. Set up `settings.py` in your django project:
   
   ```python
   INSTALLED_APPS = (
       ...,
       "privateurl",
   )
   ```

3. Add `url` Pattern in `urls.py`:
   
   ```python
   urlpatterns = [
       ...
       url(r'^private/', include('privateurl.urls', namespace='privateurl')),
   ]
   ```

4. Run Migrations:
   
   ```bash
   [~]$ python manage.py migrate
   ```

## Usage

First you need to create `PrivateUrl`, using the `create` Class Method::

```python
PrivateUrl.create(
    action, user=None, data=None, hits_limit=1, expire=None, auto_delete=False, token_size=None, replace=False)
```

where:

* `action` - is a slug that using in url and allow distinguish one url of another
* `user` - is user instance that you can get in request process
* `expire` - is expiration date for private url. You can set `datetime` or `timedelta`
* `data` - is additional data that will be saved as JSON. Setting a dict object is good idea
* `hits_limit` - is limit of requests. Set 0 for unlimit
* `auto_delete` - set `True` if you want remove private url object when it will be not available
* `token_size` - set length of token. You can set number of size or tuple with min and max size. Keep `None` for using value from `settings.PRIVATEURL_DEFAULT_TOKEN_SIZE`
* `replace` - set `True` if you want remove old exists private url for user and action before creating one
* `dashed_piece_size` - split token with dash every N symbols. Keep `None` for using value from `settings.PRIVATEURL_DEFAULT_TOKEN_DASHED_PIECE_SIZE`

For Example:

```python
from privateurl.models import PrivateUrl

purl = PrivateUrl.create("registration-confirmation", user=user)
user.send_email(
    subject="Registration confirmation",
    body=f"Follow the link for confirm your registration: {purl.get_absolute_url()}")
```

For catching Private URL Request you have to create a Receiver for the `privateurl_ok` and/or `privateurl_fail` Signal(s):

```python
from django.dispatch import receiver

from privateurl.models import PrivateUrl
from privateurl.signals import (
    privateurl_ok,
    privateurl_fail)

@receiver(privateurl_ok, sender=PrivateUrl)
def registration_confirm(sender, request, obj, action, **kwargs):
    if action != "registration-confirmation":
        return
    if obj.user:
        obj.user.registration_confirm(request=request)


@receiver(privateurl_fail, sender=PrivateUrl)
def registration_confirm_fail(sender, request, obj, action, **kwargs):
    if action != "registration-confirmation":
        return
    if obj:
        # Private URL has expired or has exceeded `hits_limit`.
        pass
    else:
        # Private URL doesn't exists, or Token is not correct.
        pass
```

After processing `privateurl_ok` signal will be redirected to root page `/`.

After processing `privateurl_fail` signal will be raised `Http404` exception.

If you want change this logic you can return `dict` with key `response` in receiver:

```python
from django.shortcuts import (
    redirect,
    render)
from django.dispatch import receiver

from privateurl.models import PrivateUrl
from privateurl.signals import (
    privateurl_ok,
    privateurl_fail)

@receiver(privateurl_ok, sender=PrivateUrl)
def registration_confirm(sender, request, obj, action, **kwargs):
    if action != "registration-confirmation":
        return
    if obj.user:
        obj.user.registration_confirm(request=request)
        obj.user.login()
    return {
        "response": redirect("user_profile"),
    }

@receiver(privateurl_fail, sender=PrivateUrl)
def registration_confirm_fail(sender, request, obj, action, **kwargs):
    if action != "registration-confirmation":
        return
    return {
        "response": render(request, "error_pages/registration_confirm_fail.html", status=404)
    }
```

# Settings

`PRIVATEURL_URL_NAMESPACE` - namespace that you setted in `urls.py`. By default it is `privateurl`.
`PRIVATEURL_DEFAULT_TOKEN_SIZE` - default size of token that will be generated using `create` or `generate_token` methods. By default it is `(8, 64)`.
