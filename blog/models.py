from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from django.dispatch import receiver

# Create your models here.


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1)  # Add this field

    def __str__(self):
        return self.title

@receiver([post_save, post_delete], sender=BlogPost)
def clear_cache_on_change(sender, **kwargs):
    cache.clear()  # Clears all cache (adjust if needed for selective clearing)