from django import forms
from .models import UserProfile
from django.contrib.auth.models import User


class Meta:
    model = UserProfile
    fields = ['profile_picture', 'bio', 'fitness_goals', 'height', 'weight', 'date_of_birth']
    labels = {
        'bio': 'Tell us about yourself',
        'fitness_goals': 'Your fitness goals',
    }
    help_texts = {
        'height': 'Enter height in cm',
        'weight': 'Enter weight in kg',
    }
    widgets = {
        'bio': forms.Textarea(attrs={'rows': 4}),
        'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
    }
