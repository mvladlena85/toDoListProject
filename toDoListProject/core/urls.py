from django.urls import path

from toDoListProject.core.views import UserRegistrationView, LoginView

urlpatterns = [
    path('signup', UserRegistrationView.as_view()),
    path('login', LoginView.as_view()),
]

