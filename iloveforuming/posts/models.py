from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
def split_sequence(sequence):
    if not sequence: 
        return []
    
    return [sequence[i*2]+sequence[i*2+1] for i in range(int(len(sequence)/2))]
class Tag(models.Model):
    name=models.CharField(max_length=50,unique=True)
    def __str__(self):
        return self.name
    
class Post(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE,related_name="posts")
    prompt=models.CharField(max_length=500) # So, the way i want to do this is the model recognising the words in english from a sentence, maybe turning them into their default forms, and then typing all of them in a list, and chekcing for it. 
    timestamp=models.DateTimeField(auto_now_add=True)
    symbols=models.CharField(max_length=500) #Think we will do ASCII printable characters (32-127) for symbol storage
    guess_count=models.IntegerField() #how many guesses does it have currently. 
    def __str__(self):
        return f"posted by {self.author} at {self.timestamp}"
    def get_symbol_codes(self):
        return split_sequence(self.symbols)
    def get_symbol_indices(self):
        """Convert codes to indices for debugging"""
        chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        indices = []
        for code in self.get_symbol_codes():
            if len(code) == 2:
                idx = chars.index(code[0]) * 62 + chars.index(code[1])
                indices.append(idx)
        return indices

class Guess(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE,related_name="guesses")
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name="guesses")
    timestamp=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"guess by {self.author} at {self.timestamp}"
class Comment(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE,related_name="comments")
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name="comments")
    symbols=models.CharField(max_length=500)
    timestamp=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"comment by {self.author.username} on post {self.post.id}"
    def get_symbol_codes(self):
        return split_sequence(self.symbols)
class Profile(models.Model): #A replacement for the default user. 
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    points = models.IntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile when a new User is created"""
    if created:
        Profile.objects.create(user=instance)
#username: admin
#password: admin