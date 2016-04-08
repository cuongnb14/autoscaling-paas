from django.contrib.auth.models import User, Group
from apiv1.models import *
from rest_framework import serializers
from apiv1.utils import *
import traceback

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',)

class WebAppSerializer(serializers.ModelSerializer):
    # status = serializers.SerializerMethodField('get_status')
    # defautl it is get_cpus method
    instances = serializers.SerializerMethodField()

    def get_instances(self, app):
        try:
            marathon_client = get_marathon_client()
            marathon_app = marathon_client.get_app("app-"+app.uuid)
            return marathon_app.instances
        except Exception as e:
            return 0

    class Meta:
        model = WebApp
        fields = ('name', 'github_url', 'min_instances', 'max_instances', 'env_hostname',"env_port","env_db_hostname","env_db_port","env_db_name","env_db_username","env_db_password","cpus","status","mem","instances", "autoscaling")

class DatabaseAppSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    def get_status(self, database_app):
        try:
            mc = get_marathon_client()
            mc.get_app("{}.database.{}".format(database_app.user.username,database_app.id))
            return "running"
        except Exception as e:
            return "not running"

    class Meta:
        model = DatabaseApp
        fields = ('id', 'host', 'port', 'root_password', 'status')
        #depth = 1

class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ('id', 'metric_type', 'upper_threshold','lower_threshold','instances_out','instances_in','scale_up_wait','scale_down_wait','disabled')

class MessageSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=45)
    message = serializers.CharField(max_length=256)
