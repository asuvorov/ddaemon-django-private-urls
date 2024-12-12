# ddaemon-django-private-url (Fork)

## Project Description

The Application helps to easy and flexibly implement the different Features, that require a Use of a Private URL for Users, like Registration Confirmation, Password Recovery, Access to a paid Content, and so on.

Low Level API provides a full Control and allows:

- limiting a Usage of the Private URL by Time and Hits;

- automatic removing Private URLs, that cannot be used anymore;

- knowing a Number of Hits, Dates of first and last Hit for each Private URL;

- controlling the Token Generator;

- saving an additional Data in JSON Format;

- processing the succeeded or failed Hits, using Django Signals, and controlling the Server Responses;

## Installation

1. Install `ddaemon-django-private-url` via `pip`: `pip install ddaemon-django-private-url`;

2. Set up `settings.py` in your Django Project:
   
   ```python
   INSTALLED_APPS = (
       ...,
       "privateurl",
       ...
   )
   ```

3. Add `url` Pattern in `urls.py`:
   
   ```python
   urlpatterns = [
       ...
       url(r"^private/", include("privateurl.urls", namespace="privateurl")),
       ...
   ]
   ```

4. Run Migrations:
   
   ```bash
   [~]$ python manage.py migrate
   ```

## Usage

First you need to create a `PrivateUrl` Object, using the `create()` Class Method:

```python
PrivateUrl.create(
    action, user=None, data=None, hits_limit=1, expire=None, auto_delete=False, token_size=None, replace=False)
```

where:

* `action` - is a Slug, used in Private URL;
* `user` - is an User Instance, that you can use during the Request processing;
* `data` - is an additional JSON Data;
* `hits_limit` - is a Limit of the Private URL Hits (`0` for unlimited Hits);
* `expire` - is an Expiration Date of the Private URL. It can be set as`datetime` or `timedelta` Object;
* `auto_delete` - `True` to automatically remove the Private URL, when it is not available;
* `token_size` - is a Length of a generated Token (`None` to default to the Value from `settings.PRIVATEURL_DEFAULT_TOKEN_SIZE`);
* `replace` -  `True` to remove the previously existing Private URL for the Action/User Combination, before creating a new one.



For Example:

```python
from privateurl.models import PrivateUrl

purl = PrivateUrl.create(action="registration-confirmation", user=user)
user.send_email(
    subject="Registration Confirmation",
    body=f"Follow the Link to confirm your Registration: {purl.get_absolute_url()}")
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
