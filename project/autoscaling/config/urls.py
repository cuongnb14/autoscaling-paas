"""autoscaling URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.response import Response
import apiv1
from django.views.generic import TemplateView

class SimpleStaticView(TemplateView):
    def get_template_names(self):
        return [self.kwargs.get('template_name') + ".html"]

    def get(self, request, *args, **kwargs):
        return super(SimpleStaticView, self).get(request, *args, **kwargs)

urlpatterns = [
    url(r'^api/v1/', include('apiv1.urls', namespace="apiv1")),
    url(r'^admin/', admin.site.urls),
    url(r'^(?P<template_name>\w+)$', SimpleStaticView.as_view(), name='static_view'),
    url(r'^$', TemplateView.as_view(template_name='dashboard.html')),


]

handler404 = apiv1.views.http404
