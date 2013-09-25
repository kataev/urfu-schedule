from django.contrib import admin
from django.conf.urls import patterns, include, url


# See: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#hooking-adminsite-instances-into-your-urlconf
admin.autodiscover()


# See: https://docs.djangoproject.com/en/dev/topics/http/urls/
urlpatterns = patterns('',
    # Admin panel and documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social_auth.urls')),
)

urlpatterns += patterns('schedule.parse.views',
    url(r'^$', 'index', name='index'),
    url(r'^login$', 'login', name='login'),

    url(r'^fill$', 'fill', name='fill'),
    url(r'^remove$', 'remove', name='remove'),

    url(r'^select$', 'select', name='select'),

    url(r'^login/error$', 'error', name='error'),
)

from parse.api import FacultyResource, GroupResource
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(GroupResource())

urlpatterns += patterns('',
     (r'^api/', include(v1_api.urls)),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^logout/$', 'logout', {'next_page': '/'}, name='logout'),
)
