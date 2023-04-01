from django.urls import path

from toDoListProject.bot import views

urlpatterns = [
    path("verify", views.VerifyBotView.as_view()),
    ]
