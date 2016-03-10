from django.contrib.auth.models import User, Group
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class MarathonAppSerializer(serializers.Serializer):
    id_ = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)