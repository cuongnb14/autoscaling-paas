from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
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
from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework.authentication import BasicAuthentication

# from rest_framework.decorators import parser_classes
# from rest_framework.parsers import FormParser


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

#@parser_classes((FormParser,))
class LoginView(APIView):

    def post(self, request):
        auth_user = request.data
        user = authenticate(username=auth_user.get("username"), password=auth_user.get("password"))
        if user is not None:
            # the password verified for the user
            if user.is_active:
                user_response = {'username': user.username, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name}
                msg = {"status": "success", "message": "login success", "user": user_response}
            else:
                msg = {"status": "error", "message": "The password is valid, but the account has been disabled!"}
        else:
            # the authentication system was unable to verify from rest_framework.decorators import parser_classes
            msg = {"status": "error", "message": "The username or password is not valid"}
        return JsonResponse(msg)

#@parser_classes((FormParser,))
class RegistrationView(APIView):

    def post(self, request):
        try:
            user = request.data
            user_avalible = User.objects.filter(email=user.get("email")).first()
            if user_avalible:
                msg = {"status": "error", "message": "Email already existed"}
            else:
                user_avalible = User.objects.filter(username=user.get("username")).first()
                if user_avalible:
                    msg = {"status": "error", "message": "Username already existed"}
                else:
                    new_user = User.objects.create_user(user.get("username"), user.get("email"), user.get("password"))
                    new_user.first_name = user.get("first_name")
                    new_user.last_name = user.get("last_name")
                    new_user.save()
                    msg = {"status": "success", "message": "Create user success"}
        except Exception as e:
            msg = {"status": "error", "message": str(e)}
        return JsonResponse(msg)


class WebAppView(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, app_name):
        try:
            marathon_client = get_marathon_client()

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
        return JsonResponse({"status": "error", "message": "Unserialize object!"})

    def post(self, request, app_name):
        """Create new application"""

        if app_name:
            raise PageNotFound(request.path)
        new_app = request.data
        try:
            app = WebApp()
            app_name = new_app["name"]

            if request.user.webapp_set.get(name=app_name):
                data = {"status": "error", "message": "app name {} already existed".format(app_name)}
            else:
                # for field, value in new_app.items():
                #     setattr(app,field,value)
                app.name = new_app["name"]
                app.github_url = new_app["github_url"]
                app.min_instances = new_app["min_instances"]
                app.max_instances = new_app["max_instances"]
                app.user = request.user
                app.status = "cloning"
                app.save()
                data = {"status": "success", "message": "create app {} success".format(app_name)}

        except Exception as e:
            data = {"status": "error", "message": str(e)}
            traceback.print_exc()

        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        return JsonResponse({"status": "error", "message": "Unserialize object!"})

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
        return JsonResponse({"status": "error", "message": "Unserialize object!"})

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
        return JsonResponse({"status": "error", "message": "Unserialize object!"})

class PolicyView(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)
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
        return JsonResponse({"status": "error", "message": "Unserialize object!"})

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
        return JsonResponse({"status": "error", "message": "Unserialize object!"})

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
        return JsonResponse({"status": "error", "message": "Unserialize object!"})

class DatabaseView(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, database_id):
        databases = request.user.databaseapp_set.all()
        serializer = DatabaseAppSerializer(databases, many=True)
        return Response(serializer.data)
