from django.urls import include, path
from users import views as users_views

urlpatterns = [
    path('', users_views.home, name = "home"),
    path('users/', include('users.urls')),
    path('questions/', include('questions.urls')),
    path('vault/', include('vault.urls')),
]
