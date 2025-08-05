from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class AchievementPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievement_posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='achievements/', blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Comment(models.Model):
    post = models.ForeignKey(AchievementPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievement_comments')
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on '{self.post.title}'"


class Like(models.Model):
    post = models.ForeignKey(AchievementPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievement_likes')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['post', 'user'], name='unique_like_per_user_per_post')
        ]

    def __str__(self):
        return f"{self.user.username} likes '{self.post.title}'"



