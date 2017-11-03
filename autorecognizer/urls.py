from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<camera_id>[0-9]+)/$', views.camera_detail, name='camera_detail'),
    # url(r'^run/$', views.run, name='settings'),
    url(r'^delete_camera/(?P<camera_id>[0-9]+)/$', views.remove_camera, name='delete_camera'),
    url(r'^delete_spot/(?P<camera_id>[0-9]+)/$', views.remove_parking_spot, name='delete_spot'),
]
