from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login$', views.LoginView.as_view(), name='login'),
    url(r'^registration$', views.RegistrationView.as_view(), name='registration'),
    url(r'^apps(/(?P<app_name>[\w_0-9\-]*))?$', views.WebAppView.as_view(), name='apps'),
    url(r'^apps(/(?P<app_name>[\w_0-9\-]*)/policies(/(?P<policy_id>\w*))?)?$', views.PolicyView.as_view(), name='policy_app'),
]
