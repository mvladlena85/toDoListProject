from django.urls import path

from toDoListProject.core.views import UserRegistrationView, LoginView, UpdateUserView, PasswordUpdateView

app_name = 'toDoListProject'
urlpatterns = [
    path('signup', UserRegistrationView.as_view(), name="register_new_user"),
    path('login', LoginView.as_view(), name="login"),
    path('profile', UpdateUserView.as_view(), name="user_details"),
    path('update_password', PasswordUpdateView.as_view(), name="change_password"),
]

