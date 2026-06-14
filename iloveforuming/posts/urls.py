from django.urls import path
from . import views
urlpatterns = [
    path('', views.post_list, name='post_list'), #this would be the home page
    path('post/create/', views.post_create, name='post_create'), #this is the create post page
]