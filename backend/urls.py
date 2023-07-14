from django.urls import path
from api import views

urlpatterns = [
    path('process_image', views.process_image),
    # path('register', views.register),
    # path('get_result', views.get_result), 
]
