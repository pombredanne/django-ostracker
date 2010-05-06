from django.conf.urls.defaults import *

urlpatterns = patterns('ostracker.views',
   url(r'^$', 'index', name='ostracker_index'),
   url(r'^project/(?P<name>[-\w]+)/$', 'project', name='ostracker_project'),
)
