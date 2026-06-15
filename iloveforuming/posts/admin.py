from django.contrib import admin
from .models import Post,Tag,Comment,Profile
# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display=('id',"author","timestamp","prompt","symbols","guess_count")
    list_filter=("timestamp",)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'timestamp')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','points','is_blocked','created_at')
    list_filter=('points','is_blocked','created_at')