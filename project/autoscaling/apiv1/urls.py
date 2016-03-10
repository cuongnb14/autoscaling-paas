from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^users$', views.User.as_view(), name='users'),
]