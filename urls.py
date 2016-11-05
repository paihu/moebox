from django.conf.urls import url

from . import views

app_name = 'moebox'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^content/(?P<request_id>[0-9]+)/delete$',
        views.delete, name='delete'),
    url(r'^content/(?P<request_id>[0-9]+)/download$',
        views.download, name='download'),
    url(r'^page/(?P<page_id>[0-9])*/?$', views.page, name='page'),
    url(r'^upload$', views.upload, name='upload'),
]
