from django.db import models
from .models import CelestialProfile, User

class Chat(models.Model):
    match = models.ForeignKey('Match', on_delete=models.CASCADE)
    initiated_at = models.DateTimeField(auto_now_add=True)
    
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10)  # 'user' or 'celestial'
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)