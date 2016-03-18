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
from django.http import Http404
from django.http import JsonResponse
from rest_framework.exceptions import APIException
import traceback
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

def http404(request):
    return JsonResponse({
        'status': "404",
        'error': 'URI not found: {}'.format(request.path)
    })

class PageNotFound(APIException):
    status_code = 404
    default_detail = 'URI not found'
    def __init__(self, path):
        if path:
             self.detail = self.default_detail + ": " + path
        else:
             self.detail = self.default_detail


class LoginView(APIView):
    def post(self, request):
        return Response("Unserialize object!")

@permission_classes((IsAuthenticated,))
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
        if app_name:
            raise PageNotFound(request.path)
        new_app = request.data
        try:
            app = WebApp()
            app_name = new_app["name"]
            if app_name.startswith(request.user.username):
                if WebApp.objects.filter(name=app_name):
                    data = {"status": "error", "message": "app name {} already existed".format(app_name)}
                else:
                    for field, value in new_app.items():
                        setattr(app,field,value)
                    app.user = request.user
                    app.save()
                    data = {"status": "success", "message": "create app {} success".format(app_name)}
            else:
                data = {"status": "error", "message": "app name must start with your's username_"}
        except Exception as e:
            data = {"status": "error", "message": str(e)}
            traceback.print_exc()

        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response("Unserialize object!")

    def put(self, request, app_name):
        try:
            marathon_client = get_marathon_client()
            action = request.data['action']
            app = request.user.webapp_set.get(name=app_name)
            data = None
            if app is None:
                data = {"status": "error", "message": "app `{}` dose not existed".format(app_name)}
            else:
                if action == "autoscaling":
                    data = {"status": "success", "message": "autoscaling to {} success".format(request.data['value'])}
                elif action == "restart":
                    marathon_client.restart_app(app_name)
                    data = {"status": "success", "message": "restarting app {}".format(app_name)}
                elif action == "stop":
                    marathon_client.scale_app(app_name, 0, force=True)
                    data = {"status": "success", "message": "stoping app {}".format(app_name)}
                elif action == "start":
                    marathon_client.scale_app(app_name, app.min_instances)
                    data = {"status": "success", "message": "starting app {}".format(app_name)}
                elif action == "scale":
                    instances = request.data["value"]
                    if instances > app.max_instances or instances < app.min_instances:
                        data = {"status": "error", "message": "number instances must in [{},{}]".format(app.min_instances, app.max_instances)}
                    else:
                        marathon_client.scale_app(app_name, instances)
                        data = {"status": "success", "message": "scaling app {}".format(app_name)}
                else:
                    data = {"status": "error", "message": "action not found"}
        except Exception as e:
            data = {"status": "error", "message": str(e)}
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response("Unserialize object!")

    def delete(self, request, app_name):
        try:
            marathon_client = get_marathon_client()
            app = request.user.webapp_set.get(name=app_name)
            if app is None or app.user.id is not request.user.id:
                data = {"status": "error", "message": "app {} does not exist".format(app_name)}
            else:
                app.delete()
                try:
                    marathon_client.delete_app(app_name,force=True)
                except:
                    pass
                data = {"status": "success", "message": "delete app {} success".format(app_name)}
        except WebApp.DoesNotExist as e:
            data = {"status": "error", "message": "app {} does not exist".format(app_name)}

        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response("Unserialize object!")

@permission_classes((IsAuthenticated,))
class PolicyView(APIView):

    def get(self, request, app_name, policy_id):
        try:
            app = request.user.webapp_set.get(name=app_name).first()
            if app is None:
                data = {"status": "error", "message": "app {} does not exist".format(app_name)}
                serializer = MessageSerializer(data=data)
            else:
                policies = app.policy_set.all()
                serializer = PolicySerializer(policies, many=True)
        except Exception as e:
            data = {"status": "error", "message": str(e)}
            serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response("Unserialize object!")

    def post(self, request, app_name, policy_id):
        new_policy = request.data
        try:
            policy = Policy()
            for field, value in new_policy.items():
                setattr(policy,field,value)
            app = request.user.webapp_set.get(name=app_name).first()
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
        if serializer.is_valid():
            return Response(serializer.data)
        return Response("Unserialize object!")

    def delete(self, request, app_name, policy_id):
        app = request.user.webapp_set.get(name=app_name).first()
        if app is None:
            serializer = get_message_serializer("error", "app {} does not exist".format(app_name))
        else:
            policy = app.policy_set.get(pk=policy_id)
            if policy == None:
                serializer = get_message_serializer("error", "policy id {} does not exist".format(policy_id))
            else:
                policy.delete()
                serializer = get_message_serializer("success", "policy id {} deleted".format(policy_id))
        if serializer.is_valid():
            return Response(serializer.data)
        return Response("Unserialize object!")
