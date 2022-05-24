from django.urls import include, path
from . import views

app_name = 'vault'
urlpatterns = [
    path('', views.two_factor_auth, name = "2fa"),
    path('passwords/', views.show_passwords, name = "passwords"),
    path('passwords/purge/', views.purge_passwords, name = "purge"),
    path('passwords/reset/', views.reset_2fa, name = "reset"),
]