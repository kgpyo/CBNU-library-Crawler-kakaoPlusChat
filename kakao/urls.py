from django.urls import path
from . import views

urlpatterns = [
    path('keyboard', views.keyboard),
    path('message', views.answer),
    path('chat_room/<user_key>', views.remove_data),
    path('get/images/<image_name>', views.get_image)
]