from django.conf.urls import url

from .views import HomeView, EmailCreateView, eventView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^new/$', EmailCreateView.as_view(), name='new'),
    url(r'^event/(?P<uuid>[0-9a-f-]+)/(?P<event>\w+)/(?P<recipient>[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)/$', eventView, name='event')
]