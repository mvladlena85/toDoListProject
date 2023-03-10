from django.urls import path

from toDoListProject.core.views import UserRegistrationView, LoginView, UpdateUserView, PasswordUpdateView

urlpatterns = [
    path('signup', UserRegistrationView.as_view()),
    path('login', LoginView.as_view()),
    path('profile', UpdateUserView.as_view()),
    path('update_password', PasswordUpdateView.as_view()),
]

