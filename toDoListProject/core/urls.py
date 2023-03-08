from django.urls import path

from toDoListProject.core.views import UserRegistrationView

urlpatterns = [
    path('signup', UserRegistrationView.as_view())
]
