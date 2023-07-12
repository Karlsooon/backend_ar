from django.urls import path
from api import views

urlpatterns = [
    path('process_image', views.process_image)
    # path('get_result', views.get_result), 
]
