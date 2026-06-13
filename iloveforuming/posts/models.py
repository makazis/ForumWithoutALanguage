from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Tag(models.Model):
    name=models.CharField(max_length=50,unique=True)
    def __str__(self):
        return self.name
    
class Post(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE,related_name="posts")
    prompt=models.CharField(max_length=500) # So, the way i want to do this is the model recognising the words in english from a sentence, maybe turning them into their default forms, and then typing all of them in a list, and chekcing for it. 
    timestamp=models.DateTimeField(auto_now_add=True)
    symbols=models.CharField(max_length=500) #Think we will do ASCII printable characters (32-127) for symbol storage
    def __str__(self):
        return f"posted by {self.author} at {self.timestamp}"
class Comment(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE,related_name="comments")
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name="comments")
    symbols=models.CharField(max_length=500)
    timestamp=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"comment by {self.author.username} on post {self.post.id}"
#username: admin
#password: admin