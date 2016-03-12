from django.conf.urls import url
from . import views

urlpatterns = [
    # /apps,    /apps/<app_name>
    url(r'^apps(/(?P<app_name>\w*))?$', views.WebAppView.as_view(), name='apps'),
    # /apps/<app_name>/policies,    /apps/<app_name>/policies/<policy_id>
    url(r'^apps(/(?P<app_name>\w.*)/policies(/(?P<policy_id>\w*))?)?$', views.PolicyView.as_view(), name='policy_app'),
]
