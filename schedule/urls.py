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

urlpatterns += patterns('schedule.apps.core.views',
    url(r'^$', 'index'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^logout/$', 'logout', {'next_page': '/'}, name='logout'),
)
