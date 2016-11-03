# Uploader script like sunuploader.

## Install

* pip install dango
* django-admin startproject projectname
* cd projectname
* git clone https://github.com/paihu/moebox.git
* edit prjectname/settings.py
```
INSTALLED_APPS = {
    'moebox.apps.MoeboxConfig',
    ...
}
```
* edit projectname/urls.py
```
from django.conf.urls import include
...
urlpatterns = [
    url(r'moebox/', include('moebox.urls'), name='moebox')
    ...
]
```
* python manage.py migrations moebox
* python manage.py migrate

