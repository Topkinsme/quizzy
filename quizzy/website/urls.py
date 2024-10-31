from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("entercode",views.entercode,name="entercode"),
]