from django.contrib import admin
from .models import Post,Tag,Comment
# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display=('id',"author","timestamp","prompt","symbols","guess_count")
    list_filter=("timestamp",)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'timestamp')