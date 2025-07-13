from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class SentimentAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    sentiment = models.CharField(max_length=8)
    confidence = models.FloatField()
    raw_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']