from django.contrib.auth import views as auth_views
from django.urls import include, path
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name = "login"),
    path('logout/', auth_views.LogoutView.as_view(), name = "logout"),
    path("signup/", views.SignUp.as_view(), name = "signup"),
    path("recover/", views.recover, name = "recover"),
]