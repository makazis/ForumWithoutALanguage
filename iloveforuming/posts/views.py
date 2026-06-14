from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q, F
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import Post, Tag, Guess, Comment

# Create your views here.
def post_list(request):
    #we get some posts depending on the query, either by time, or by least guessed on
    posts = Post.objects.all().order_by('-timestamp')

    least_guessed = request.GET.get('least_guessed')
    if least_guessed:
        posts = posts.annotate(guess_count=Count('guesses')).order_by('guess_count')
    #we get a paginator with 10 posts in a page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'posts/post_list.html', {'page_obj': page_obj})

@login_required
def post_create(request):
    """Create a new post (with prompt + symbol sequence + intended tags)"""
    all_tags = Tag.objects.all()
    
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        symbols = request.POST.get('symbols')
        ##intended_tag_ids = request.POST.getlist('intended_tags')
        
        if not prompt or not symbols:
            messages.error(request, "Please fill in all fields")
            return render(request, 'posts/post_create.html', {'all_tags': all_tags})
        
        post = Post.objects.create(
            author=request.user,
            prompt=prompt,
            symbols=symbols,
            guess_count=0
        )
        messages.success(request, "Post created successfully! Others will now try to guess your meaning.")
        return redirect('post_detail', post_id=post.id)
    
    return render(request, 'posts/post_create.html', {'all_tags': all_tags})