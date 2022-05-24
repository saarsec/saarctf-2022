from django.urls import path

from . import views

app_name = 'questions'
urlpatterns = [
    path('', views.questions, name = 'questions'),
    path('reset/', views.reset, name = 'reset'),
    path('shared/', views.shared_questions, name = 'shared'),
]