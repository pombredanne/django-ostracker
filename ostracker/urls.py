from django.conf.urls.defaults import *

urlpatterns = patterns('ostracker.views',
   url(r'^$', 'index', name='index'),
   url(r'^summary/$', 'summary', name='summary'),
   url(r'^activity/$', 'activity', name='activity'),
   url(r'^project/(?P<name>[-\w]+)/$', 'project', name='project'),
)
