from django.contrib.auth.models import User, Group
from apiv1.models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',)

class WebAppSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    min_instances = serializers.IntegerField()
    max_instances = serializers.IntegerField()
    status = serializers.CharField(max_length=10)
    port = serializers.IntegerField(allow_null=True)
    cpus = serializers.FloatField(allow_null=True)
    mem = serializers.FloatField(allow_null=True)
    instances = serializers.IntegerField(allow_null=True)

class DatabaseAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseApp
        fields = ('id', 'host', 'port', 'mysql_version',)

class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ('id', 'metric_type', 'upper_threshold','lower_threshold','instances_out','instances_in','scale_up_wait','scale_down_wait','disabled')

class MessageSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=45)
    message = serializers.CharField(max_length=256)
