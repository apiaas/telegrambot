from django.conf.urls import url
from document.views import document_list
from document.views import document_detail
from document.views import document_search
from django.conf import settings


urlpatterns = [

    url('api/document/document/$', document_list, name='api_document_list'),
    url('api/document/document/(?P<pk>\d+)/$', document_detail, name='api_document_detail'),
    url(r'^search/', document_search, name='document_search'),
    url(r'^m/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
]
