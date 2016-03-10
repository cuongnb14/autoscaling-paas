from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth import models
import json 
from apiv1.serializers import UserSerializer, MarathonAppSerializer
from django.core import serializers
from rest_framework import viewsets


# Create your views here.
class User(APIView):
    """docstring for ClassName"""
    def get(self, request):
        users = models.User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = {"id": "1", "name": "bot"}
        serializer = MarathonAppSerializer(data={"id_": "1", "name": "bot"})
        serializer.is_valid()
        return Response(serializer.data)


