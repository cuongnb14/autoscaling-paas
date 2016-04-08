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
import os
import uuid
import shutil
import threading
from django.db.models import Max
from influxdb.influxdb08 import InfluxDBClient
import time
from django.conf import settings
from datetime import datetime

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
                serializer = WebAppSerializer(app)
            else:
                apps = request.user.webapp_set.all()
                serializer = WebAppSerializer(apps, many=True)
        except WebApp.DoesNotExist as e:
            traceback.print_exc()
            msg = {"status": "error", "message": "app {} does not exist".format(app_name)}
            return JsonResponse(msg)
        except Exception as e:
            traceback.print_exc()
            msg = {"status": "error", "message": str(e)}
            return JsonResponse(msg)

        return Response(serializer.data)

    def post(self, request, app_name):
        """Create new application"""

        if app_name:
            raise PageNotFound(request.path)
        new_app = request.data
        try:
            app = WebApp()
            app_name = new_app["name"]

            if request.user.webapp_set.filter(name=app_name):
                data = {"status": "error", "message": "app name {} already existed".format(app_name)}
            else:
                app.name = new_app["name"]
                app.github_url = new_app["github_url"]
                app.min_instances = new_app["min_instances"]
                app.max_instances = new_app["max_instances"]
                app.cpus = new_app["cpus"]
                app.mem = new_app["mem"]
                app.env_hostname = get_setting("env_hostname", "10.10.10.51")

                max_port = WebApp.objects.all().aggregate(Max('env_port'))["env_port__max"]
                if max_port and max_port >= int(get_setting("min_app_port", "31300")):
                    new_port = max_port + 1
                    if new_port > int(get_setting("max_app_port", "31399")):
                        msg = {"status": "error", "message": "Unavalible resource"}
                        return JsonResponse(msg)
                else:
                    new_port = int(get_setting("min_app_port", "31300"))

                app.env_port = new_port
                app.env_db_hostname = new_app["env_db_hostname"]
                app.env_db_port = new_app["env_db_port"]
                app.env_db_name = new_app["env_db_name"]
                app.env_db_username = new_app["env_db_username"]
                app.env_db_password = new_app["env_db_password"]
                app.user = request.user
                app.status = "cloning"
                app.uuid = str(uuid.uuid4())
                app.save()

                cloning = threading.Thread(target=self.__cloning, args=(app,), daemon=True)
                cloning.start()

                data = {"status": "success", "message": "create app {} success, app is cloning".format(app_name)}

        except Exception as e:
            data = {"status": "error", "message": str(e)}
            traceback.print_exc()

        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        return JsonResponse({"status": "error", "message": "Unserialize object!"})

    def __deploy_app(self, app):
        marathon_client = get_marathon_client()
        app_template = get_setting("app_template")
        app_json = app_template % {
                                    "uuid": app.uuid,
                                    "cpus": app.cpus,
                                    "mem": app.mem,
                                    "service_port": app.env_port,
                                    "env_port": app.env_port,
                                    "env_hostname": app.env_hostname,
                                    "env_db_hostname": app.env_db_hostname,
                                    "env_db_port": app.env_db_port,
                                    "env_db_name": app.env_db_name,
                                    "env_db_username": app.env_db_username,
                                    "env_db_password": app.env_db_password}

        try:
            try:
                marathon_client.delete_app("app-"+app.uuid, force=True )
                time.sleep(5)
            except Exception as e:
                pass
            app_marathon = get_marathon_app(app_json)
            marathon_client.create_app(app_marathon.id, app_marathon)
            app.status = "deploying"
            msg = {"status": "success", "message": "deploying app {}".format(app.name)}
        except Exception as e:
            msg = {"status": "error", "message": "Unknown error"}
        return msg


    def __cloning(self, app):
        try:
            app_dir = get_app_dir(app)
            if os.path.isdir(app_dir):
                shutil.rmtree(app_dir)

            os.system("git clone {} {}".format(app.github_url, app_dir))
            app.status = "cloned"
            self.__deploy_app(app)
        except Exception as e:
            app.status = "clone failed"
        app.save()

    def put(self, request, app_name):
        try:
            marathon_client = get_marathon_client()
            action = request.data['action']
            app = request.user.webapp_set.get(name=app_name)
            data = None
            if app is None:
                data = {"status": "error", "message": "app `{}` dose not existed".format(app_name)}
            else:
                if action == "info":
                    new_info = request.data
                    app.min_instances = new_info["min_instances"]
                    app.max_instances = new_info["max_instances"]
                    app.cpus = new_info["cpus"]
                    app.mem = new_info["mem"]
                    app.env_db_hostname = new_info["env_db_hostname"]
                    app.env_db_port = new_info["env_db_port"]
                    app.env_db_name = new_info["env_db_name"]
                    app.env_db_username = new_info["env_db_username"]
                    app.env_db_password = new_info["env_db_password"]
                    app.save()
                    data = {"status": "success", "message": "Update info {} success".format(app_name)}
                elif action == "autoscaling":
                    app.autoscaling = not app.autoscaling
                    data = {"status": "success", "message": "autoscaling toggle success"}
                    app.save()
                elif action == "restart":
                    marathon_client.restart_app(app_name)
                    data = {"status": "success", "message": "restarting app {}".format(app_name)}
                elif action == "stop":
                    marathon_client.scale_app("app-"+app.uuid, 0, force=True)
                    data = {"status": "success", "message": "stoping app {}".format(app_name)}
                elif action == "start":
                    marathon_client.scale_app("app-"+app.uuid, app.min_instances)
                    data = {"status": "success", "message": "starting app {}".format(app_name)}
                elif action == "scale":
                    instances = request.data["value"]
                    if instances > app.max_instances or instances < app.min_instances:
                        data = {"status": "error", "message": "number instances must in [{},{}]".format(app.min_instances, app.max_instances)}
                    else:
                        marathon_client.scale_app("app-"+app.uuid, instances)
                        data = {"status": "success", "message": "scaling app {} to {}".format(app_name, instances)}
                elif action == "deploy":
                    try:
                        data = self.__deploy_app(app)
                    except Exception as e:
                        data = {"status": "error", "message": "Unknown error"}
                else:
                    data = {"status": "error", "message": "Action not found"}
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
                try:
                    marathon_client.delete_app("app-".app.uuid,force=True)
                except Exception as e:
                    pass
                try:
                    app_dir = get_app_dir(app)
                    if os.path.isdir(app_dir):
                        shutil.rmtree(app_dir)
                except Exception as e:
                    raise
                app.delete()
                data = {"status": "success", "message": "delete app {} success".format(app_name)}
        except WebApp.DoesNotExist as e:
            data = {"status": "error", "message": "app {} does not exist".format(app_name)}
        except Exception as e:
            data = {"status": "error", "message": "Unknown error"}

        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        return JsonResponse({"status": "error", "message": "Unserialize object!"})

class PolicyView(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, app_name, policy_id):
        try:
            app = request.user.webapp_set.get(name=app_name)
            if app is None:
                msg = {"status": "error", "message": "app {} does not exist".format(app_name)}
                return JsonResponse(msg)
            else:
                policies = app.policy_set.all()
                serializer = PolicySerializer(policies, many=True)
                return Response(serializer.data)
        except Exception as e:
            msg = {"status": "error", "message": str(e)}
            return JsonResponse(msg)

    def post(self, request, app_name, policy_id):
        new_policy = request.data
        new_policy = dict(new_policy)
        new_policy.pop("id", None)
        try:
            policy = Policy()
            for field, value in new_policy.items():
                setattr(policy,field,value)
            app = request.user.webapp_set.get(name=app_name)
            policy.web_app = app
            policy.save()
            msg = {"status": "success", "message": "add policy for app {} success".format(app_name)}
        except Exception as e:
            msg = {"status": "error", "message": str(e)}
        return JsonResponse(msg)

    def put(self, request, app_name, policy_id):
        data = request.data
        data = dict(data)
        try:
            app = request.user.webapp_set.get(name=app_name)
            policy = app.policy_set.get(pk=policy_id)
            data.pop("id", None)
            for field, value in data.items():
                setattr(policy,field,value)
            policy.save()
            # policy.metric_type = data["metric_type"]
            # policy.upper_threshold = data["upper_threshold"]
            # policy.lower_threshold = data["lower_threshold"]
            # policy.instances_out = data["instances_out"]
            # policy.instances_in = data["instances_in"]
            # policy.scale_up_wait = data["scale_up_wait"]
            # policy.scale_down_wait = data["scale_down_wait"]
            msg = {"status": "success", "message": "Update policy success"}


        except Exception as e:
            msg = {"status": "error", "message": str(e)}
            traceback.print_exc()
        return JsonResponse(msg)

    def delete(self, request, app_name, policy_id):
        try:
            app = request.user.webapp_set.get(name=app_name)
            policy = app.policy_set.get(pk=policy_id)
            policy.delete()
            msg = {"status": "success", "message": "Delete policy success"}
        except Exception as e:
            msg = {"status": "error", "message": str(e)}
        return JsonResponse(msg)

class DatabaseView(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, database_id):
        databases = request.user.databaseapp_set.all()
        serializer = DatabaseAppSerializer(databases, many=True)
        return Response(serializer.data)

    def post(self, request, database_id):
        try:
            database = DatabaseApp()
            database.host = get_setting("database_host", "10.10.10.51")
            max_port = DatabaseApp.objects.all().aggregate(Max('port'))["port__max"]
            if max_port and max_port >= int(get_setting("min_database_port", "31200")):
                new_port = max_port + 1
                if new_port > int(get_setting("max_database_port", "31299")):
                    msg = {"status": "error", "message": "Unavalible resource"}
                    return JsonResponse(msg)
            else:
                new_port = int(get_setting("min_database_port", "31200"))
            database.port = new_port
            database.user = request.user
            database.root_password = request.data["root_password"]
            database.uuid = str(uuid.uuid4())
            database.save()

            marathon_client = get_marathon_client()
            database_template = get_setting("database_template","")
            database_json = database_template % {
                                                "uuid": database.uuid,
                                                "service_port": database.port,
                                                "root_password": database.root_password
                                                }

            try:
                app_marathon = get_marathon_app(database_json)
                marathon_client.create_app(app_marathon.id, app_marathon)
                msg = {"status": "success", "message": "created and deploying database"}
            except Exception as e:
                traceback.print_exc()
                msg = {"status": "error", "message": "Unknown error when deploying database app"+str(database_json)}

        except Exception as e:
            msg = {"status": "error", "message": "Unknown error"}
            traceback.print_exc()
        return JsonResponse(msg)

    def put(self, request, database_id):
        try:
            database = request.user.databaseapp_set.get(id=database_id)
            database.root_password = request.data["new_password"]
            database.save()
            msg = {"status": "success", "message": "Change password success"}
        except Exception as e:
            msg = {"status": "error", "message": "Unknown error"}
            traceback.print_exc()
        return JsonResponse(msg)

    def delete(self, request, database_id):
        try:
            database = request.user.databaseapp_set.get(id=database_id)
            try:
                marathon_client = get_marathon_client()
                marathon_client.delete_app("database-"+database.uuid,force=True)
            except Exception as e:
                pass
            try:
                database_dir = get_database_dir(database)
                if os.path.isdir(database_dir):
                    shutil.rmtree(database_dir)
            except Exception as e:
                pass
            database.delete()

            msg = {"status": "success", "message": "Delete database success"}
        except Exception as e:
            msg = {"status": "error", "message": "Unknown error"}
            traceback.print_exc()
        return JsonResponse(msg)

class MetricView(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, app_name):
        try:
            app = request.user.webapp_set.get(name=app_name)
            now = int(datetime.now().timestamp()) # second
            end = int(request.GET.get("end", now))
            start = request.GET.get("start", end - 3600) # 1 day

            influxdb_client = InfluxDBClient(settings.INFLUXDB["HOST"], settings.INFLUXDB["PORT"], settings.INFLUXDB["USERNAME"], settings.INFLUXDB["PASSWORD"], settings.INFLUXDB["DBNAME"])
            mesos_app_id = "app-"+app.uuid

            query = "SELECT COUNT(DISTINCT(mesos_task_id)) as instances, MEAN(cpu_usage) as mean_cpu, MEAN(mem_usage) as mean_mem  "
            query += "FROM monitoring "
            query += "WHERE app_uuid = '{}' and time > {}s and time < {}s ".format(mesos_app_id, start, end)
            query += "GROUP BY time(10s)"
            metrics = influxdb_client.query(query)
            if metrics:
                return JsonResponse({"data" : metrics[0]["points"]})
                return JsonResponse({"data" : "sd"})
            else:
                return JsonResponse({"data" : query})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"data" : "11"})
