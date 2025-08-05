from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField

# Create your models here.


class UserProfile(models.Model):
    """Model to store user profile information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    fitness_goals = models.CharField(max_length=255, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = CountryField(blank_label='(select country)', blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"