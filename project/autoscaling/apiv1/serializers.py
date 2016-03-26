from django.contrib.auth.models import User, Group
from apiv1.models import *
from rest_framework import serializers
from apiv1.utils import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',)

class WebAppSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    github_url = serializers.CharField(max_length=256)
    min_instances = serializers.IntegerField()
    max_instances = serializers.IntegerField()
    env_hostname = serializers.CharField(max_length=45)
    env_port = serializers.IntegerField()
    env_db_hostname = serializers.CharField(max_length=45, allow_blank=True)
    env_db_port = serializers.IntegerField()
    env_db_name = serializers.CharField(max_length=45, allow_blank=True)
    env_db_username = serializers.CharField(max_length=45, allow_blank=True)
    env_db_password = serializers.CharField(max_length=45, allow_blank=True)
    status = serializers.CharField(max_length=10)
    cpus = serializers.FloatField(allow_null=True)
    mem = serializers.FloatField(allow_null=True)
    instances = serializers.IntegerField(allow_null=True)

class DatabaseAppSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField('set_status')

    def set_status(self, database_app):
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
