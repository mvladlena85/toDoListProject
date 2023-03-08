from django.contrib.auth import login, authenticate
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from toDoListProject.core.serializers import CreateUserSerializer, LoginSerializer


class UserRegistrationView(CreateAPIView):
    serializer_class = CreateUserSerializer


class LoginView(CreateAPIView):
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login(request=self.request, user=serializer.save())
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
