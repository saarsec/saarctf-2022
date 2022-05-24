from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('loops/<loop_id>', views.download, name='download'),
    path('loops', views.loops, name='loops'),
    path('samples', views.samples, name='samples'),
    path('synths', views.synths, name='synths'),
    path('publish/<loop_id>', views.publish, name='publish'),
    path('like/<loop_id>', views.like, name='like'),
    path('create_loop', views.create_loop, name='create_loop'),
    path('preview_loop', views.preview_loop, name='preview_loop'),
    path('sample/<sample_type>/<sample_name>', views.sample, name='sample'),
    path('new_sample', views.new_sample, name='new_sample'),
    path('synth/<synth_type>/<synth_name>', views.synth, name='synth'),
    path('new_synth', views.new_synth, name='new_synth'),
]
