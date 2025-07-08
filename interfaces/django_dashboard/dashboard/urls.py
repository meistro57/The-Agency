from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('run/', views.run_prompt, name='run_prompt'),
    path('nodes/', views.node_editor, name='node_editor'),
]
