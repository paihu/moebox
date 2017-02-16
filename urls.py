from django.conf.urls import url

from . import views

app_name = 'moebox'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^content/(?P<request_id>\d+)/delete$',
        views.delete, name='delete'),
    url(r'^content/(?P<request_id>\d+)/download$',
        views.download, name='download'),
    url(r'^list/$', views.page, name='page'),
    url(r'^upload$', views.upload, name='upload'),
]
