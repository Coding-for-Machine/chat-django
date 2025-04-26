# from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Chat(models.Model):
    PRIVATE = 'private'
    GROUP = 'group'
    CHANNEL = 'channel'

    CHAT_TYPE_CHOICES = [
        (PRIVATE, 'Private'),
        (GROUP, 'Group'),
        (CHANNEL, 'Channel'),
    ]

    chat_type = models.CharField(max_length=10, choices=CHAT_TYPE_CHOICES)
    name = models.CharField(max_length=255, blank=True, null=True)  # group/channel nomi
    description = models.TextField(blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='chats')
    admins = models.ManyToManyField(User, related_name='admin_chats', blank=True)  # group/channel adminlari
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Chat {self.id}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='messages/files/', blank=True, null=True)
    replied_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    forwarded_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='forwards')
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender.username}: {self.text[:20]}"


class Reaction(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10)  # emoji text (like 👍, ❤️, 😂)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user', 'emoji')  # Bitta user bitta emoji qo'yadi


class VideoCallSession(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='video_sessions')
    started_by = models.ForeignKey(User, on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='video_calls')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
