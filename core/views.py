from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date  #Fix added

from .models import UserProfile
from .forms import UserProfileForm
from community.models import AchievementPost

# Create your views here.


def index(request):
    latest_posts = AchievementPost.objects.order_by('-created_on')[:3]
    return render(request, 'home/index.html', {'latest_posts': latest_posts})


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    subscriptions = request.user.usersubscription_set.select_related('plan').order_by('-start_date')
    orders = request.user.order_set.order_by('-created_on')[:5]

    # Calculate age if date_of_birth is set
    if user_profile.date_of_birth:
        today = date.today()
        user_profile.age = (
            today.year - user_profile.date_of_birth.year
            - ((today.month, today.day) < (user_profile.date_of_birth.month, user_profile.date_of_birth.day))
        )

    return render(request, 'core/profile.html', {
        'user_profile': user_profile,
        'subscriptions': subscriptions,
        'orders': orders
    })


@login_required
def profile_edit(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'core/profile_edit.html', {'form': form})



