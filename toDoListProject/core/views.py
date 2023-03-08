from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView

from toDoListProject.core.serializers import CreateUserSerializer


class UserRegistrationView(CreateAPIView):
    serializer_class = CreateUserSerializer
