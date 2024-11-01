from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("createcode/", views.createcode, name="createcode"),
    path("entercode/",views.entercode,name="entercode"),
    path("questions/<str:code>",views.questions,name="questions"),
    path("delete/<str:q_code>/<str:code>",views.delete,name="delete"),
    path("quizdata/<str:code>",views.quizdata,name="delete"),
]