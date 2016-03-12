from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^apps(/(?P<app_name>\w*))?$', views.WebAppView.as_view(), name='apps'),
    url(r'^apps(/(?P<app_name>\w.*)/policies)?$', views.PolicyView.as_view(), name='policy_app'),
]