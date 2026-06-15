from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('', views.post_list, name='post_list'), #this would be the home page
    path('post/create/', views.post_create, name='post_create'), #this is the create post page
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/guess/', views.submit_guess, name='submit_guess'),
    path('user/<int:user_id>/', views.user_profile, name='user_profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    
    path('post/<int:post_id>/comment/', views.comment_create, name='comment_create'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('post/create/random/', views.post_create_random, name='post_create_random'),
    path('post/<int:post_id>/comment/', views.comment_create, name='comment_create'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('post/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('admin/post/<int:post_id>/delete/', views.admin_post_delete, name='admin_post_delete'),
    path('accounts/', include('allauth.urls')),
]
