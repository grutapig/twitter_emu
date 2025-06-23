from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets


def generate_twitter_id():
    return str(secrets.randbelow(10**19)).zfill(19)


class User(AbstractUser):
    twitter_id = models.CharField(max_length=19, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    screen_name = models.CharField(max_length=50, unique=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.twitter_id:
            self.twitter_id = generate_twitter_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"@{self.screen_name} ({self.name})"


class Community(models.Model):
    twitter_id = models.CharField(max_length=19, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.twitter_id:
            self.twitter_id = generate_twitter_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Communities"


class Tweet(models.Model):
    twitter_id = models.CharField(max_length=19, unique=True, null=True, blank=True)
    text = models.TextField(max_length=280)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tweets')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, blank=True, related_name='tweets')
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(blank=True, null=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.twitter_id:
            self.twitter_id = generate_twitter_id()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.community:
            return f"{self.community.name} - @{self.author.screen_name}: {self.text[:50]}..."
        return f"@{self.author.screen_name}: {self.text[:50]}..."

    class Meta:
        ordering = ['-created_at']
