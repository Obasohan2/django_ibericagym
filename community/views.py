from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AchievementPost, Comment, Like
from .forms import PostForm, CommentForm

def posts(request):
    all_posts = AchievementPost.objects.all().order_by('-created_at')
    return render(request, 'community/posts.html', {'posts': all_posts})

def post_detail(request, post_id):
    post = get_object_or_404(AchievementPost, id=post_id)
    comments = post.comments.all().order_by('-created_at')
    
    # Check if current user has liked the post
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = Like.objects.filter(post=post, user=request.user).exists()
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('community:post_detail', post_id=post.id)
    else:
        comment_form = CommentForm()
    
    return render(request, 'community/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user_has_liked': user_has_liked,
        'like_count': post.likes.count()
    })

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            messages.success(request, 'Your post has been created!')
            return redirect('community:post_detail', post_id=new_post.id)
    else:
        form = PostForm()
    
    return render(request, 'community/create_post.html', {'form': form})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(AchievementPost, id=post_id)
    
    # Check if user already liked the post
    like, created = Like.objects.get_or_create(
        post=post,
        user=request.user
    )
    
    if not created:
        like.delete()
    
    return redirect('community:post_detail', post_id=post.id)