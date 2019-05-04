from django.urls import path
from . import views

urlpatterns = [
    path('search/<str:library>/<str:keyword>/<str:page_number>/<str:options>', views.search_library),
    path('search/<str:library>/<str:keyword>/<str:page_number>', views.search_library),
    path('search/<str:library>/<str:keyword>', views.search_library),
    path('post/', views.search_option),
    path('location/<str:library>/<str:isbn>', views.search_book_location),
    path('all/<str:keyword>', views.search_all),
]