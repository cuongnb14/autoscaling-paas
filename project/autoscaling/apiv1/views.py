from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth import models
from apiv1.models import *
from apiv1.serializers import *
from django.core import serializers
from rest_framework import viewsets
from apiv1.utils import *
import json
# Create your views here.

class WebAppView(APIView):
    def get(self, request, app_name):
        try:
            marathon_client = get_marathon_client

            if app_name:
                app = request.user.webapp_set.get(name=app_name)
                app = get_info_app(app, marathon_client)
                serializer = WebAppSerializer(data=app)
            else:
                apps = request.user.webapp_set.all()
                data = []
                for app in apps:
                    app = get_info_app(app, marathon_client)
                    data.append(app)
                serializer = WebAppSerializer(data=data, many=True)
        except WebApp.DoesNotExist as e:
            data = {"status": "error", "message": "app {} does not exist".format(app_name)}
            serializer = MessageSerializer(data=data)
        except Exception as e:
            data = {"status": "error", "message": str(e)}
            serializer = MessageSerializer(data=data)

        if serializer.is_valid():
            return Response(serializer.data)
        return Response("Unserialize object!")

    def post(self, request, app_name):
        new_app = request.data
        try:
            app = WebApp()
            app_name = new_app["name"]
            if app_name.startswith(request.user.username):
                if WebApp.objects.filter(name=app_name):
                    data = {"status": "error", "message": "app name {} already existed".format(app_name)}
                else:
                    app.name = new_app["name"]
                    app.min_instances = new_app["min_instances"]
                    app.max_instances = new_app["max_instances"]
                    app.github_url = new_app["github_url"]
                    app.user = request.user
                    app.save()
                    data = {"status": "success", "message": "create app {} success".format(app_name)}
            else:
                data = {"status": "error", "message": "app name must start with your's username_"}
        except Exception as e:
            data = {"status": "error", "message": str(e)}

        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response("Unserialize object!")

    def delete(self, request, app_name):
        marathon_client = get_marathon_client()
        app = WebApp.objects.filter(name=app_name).first()
        if app is None or app.user.id is not request.user.id:
            data = {"status": "error", "message": "app {} does not exist".format(app_name)}
        else:
            app.delete()
            data = {"status": "success", "message": "delete app {} success".format(app_name)}
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response("Unserialize object!")

class PolicyView(APIView):

    def get(self, request, app_name):
        try:
            app = WebApp.objects.filter(name=app_name)[0]
            policies = app.policy_set.all()
            serializer = PolicySerializer(policies, many=True)
        except IndexError as e:
            data = {"status": "error", "message": "app {} does not exist".format(app_name)}
            serializer = MessageSerializer(data=data)
            serializer.is_valid()
        return Response(serializer.data)

    def post(self, request, app_name):
        new_policy = request.data
        try:
            policy = Policy()
            for field, value in new_policy.items():
                setattr(policy,field,value)
            app = WebApp.objects.filter(name=app_name).first()
            if app is None:
                data = {"status": "error", "message": "app {} does not exist".format(app_name)}
                serializer = MessageSerializer(data=data)
            else:
                policy.web_app = app
                policy.save()
                data = {"status": "success", "message": "add policy for app {} success".format(app_name)}
        except Exception as e:
            data = {"status": "error", "message": str(e)}

        serializer = MessageSerializer(data=data)
        serializer.is_valid()
        return Response(serializer.data)
