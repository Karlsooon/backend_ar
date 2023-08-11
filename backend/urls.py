from django.urls import path
from api import views

urlpatterns = [
    path("process_image", views.process_image),
    path("chat_with_chatgpt", views.chat_with_chatgpt),
    path("search_person", views.search_person),

    # path("process_audio", views.process_audio),
    # path('register', views.register),
    # path('get_result', views.get_result),
]
