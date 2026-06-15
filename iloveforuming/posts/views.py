from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q, F
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import Post, Tag, Guess, Comment, Profile
from .random_sentences import get_random_sentence_w_multiplier

# Create your views here.
def post_list(request):
    """Display all posts with sorting and filtering options"""
    posts = Post.objects.all()
    
    # Get filter/sort parameters from URL
    sort_by = request.GET.get('sort', 'newest')
    author_filter = request.GET.get('author', None)
    
    # Apply author filter if specified
    if author_filter:
        try:
            author = User.objects.get(username=author_filter)
            posts = posts.filter(author=author)
        except User.DoesNotExist:
            pass
    
    if sort_by == 'least_guesses':
        posts = posts.annotate(guess_count2=Count('guesses')).order_by('guess_count2', '-timestamp')
    elif sort_by == 'most_guesses':
        posts = posts.annotate(guess_count2=Count('guesses')).order_by('-guess_count2', '-timestamp')
    elif sort_by == 'oldest':
        posts = posts.order_by('timestamp')
    else: 
        posts = posts.order_by('-timestamp')
    
    # Get unique authors for filter 
    authors = User.objects.filter(posts__isnull=False).distinct()
    
    # Get current author name for display
    current_author = None
    if author_filter:
        try:
            current_author = User.objects.get(username=author_filter)
        except User.DoesNotExist:
            pass
    
    context = {
        'posts': posts,
        'current_sort': sort_by,
        'authors': authors,
        'current_author': current_author,
        'author_filter': author_filter,
    }
    return render(request, 'posts/post_list.html', context)

@login_required
def post_create(request):
    """Create a new post with custom prompt"""
    if request.method == 'POST':
        #if request.user.is_blocked:
        #    messages.error(request, "YOU ARE BLOCKED FROM THE SITE!!! FOOL")
        #    return render(request, 'posts/post_create.html')
        prompt = request.POST.get('prompt')
        symbols = request.POST.get('symbols')
        if not prompt or not symbols:
            messages.error(request, "Please fill in all fields")
            return render(request, 'posts/post_create.html')
        
        post = Post.objects.create(
            author=request.user,
            prompt=prompt,
            symbols=symbols,
            multiplier=1,
        )
        
        messages.success(request, "Post created successfully!")
        return redirect('post_detail', post_id=post.id)
    
    return render(request, 'posts/post_create.html')

@login_required
def post_create_random(request):
    multiplier,random_prompt = get_random_sentence_w_multiplier()
    
    if request.method == 'POST':
        #if request.user.is_blocked:
        #    messages.error(request, "YOU ARE BLOCKED FROM THE SITE!!! FOOL")
        #    return render(request, 'posts/post_create.html')
        symbols = request.POST.get('symbols')
        multiplier=request.POST.get('multiplier')
        random_prompt=request.POST.get('random_prompt')
        if not symbols:
            messages.error(request, "Too vague, add more symbols!")
            return render(request, 'posts/post_create_random.html', {'random_prompt': random_prompt})
        
        post = Post.objects.create(
            author=request.user,
            prompt=random_prompt,
            symbols=symbols,
            multiplier=multiplier,
        )
        
        messages.success(request, f"Random post created! (x{post.multiplier} point multiplier for guessers!)")
        return redirect('post_detail', post_id=post.id)
    
    return render(request, 'posts/post_create_random.html', {'random_prompt': random_prompt,'multiplier': multiplier})

@login_required
def submit_guess(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Don't allow guessing on your own post
    if request.user == post.author:
        messages.error(request, "You cannot guess on your own post!")
        return redirect('post_detail', post_id=post.id)
    
    # Check if already guessed
    if Guess.objects.filter(author=request.user, post=post).exists():
        messages.warning(request, "You already guessed on this post!")
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        #if request.user.is_blocked:
        #    messages.error(request, "YOU ARE BLOCKED FROM THE SITE!!! FOOL")
        #    return render(request, 'posts/post_details.html')
        guessed_text = request.POST.get('guessed_words', '').strip()
        
        if not guessed_text:
            messages.error(request, "Please enter your guess")
            return redirect('post_detail', post_id=post.id)
        
        prompt_words = set(post.get_prompt_words())
        
        r=guessed_text.split(" ")
        guessed_words =[i.lower().strip(",.;-!?") for i in r]
        
        
        correct_words = list(prompt_words.intersection(guessed_words))
        score = len(correct_words) * post.multiplier
        
        guess = Guess.objects.create(
            author=request.user,
            post=post,
            guessed_words=guessed_text,
            correct_words=correct_words,
            score_earned=score,
        )
        

        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.points += score
        profile.save()
        
        
        author_profile, _ = Profile.objects.get_or_create(user=post.author)

        author_points = int(score / 2) #They get half of the points, cuz good post
        author_profile.points += author_points
        author_profile.save()
        post.save()
        

        if score > 0:
            multiplier_text = f" (x{post.multiplier} multiplier!)" if post.multiplier > 1 else ""
            messages.success(
                request, 
                f" You got {len(correct_words)} correct word(s)! +{score} points{multiplier_text}"
            )
            if len(correct_words) < len(prompt_words):
                missing = len(prompt_words) - len(correct_words)
                messages.info(request, f"You missed {missing} word(s). Try another vague-post!")
        else:
            messages.info(request, "Fool! You have no idea what you're talking about.")
        
    return redirect('post_detail', post_id=post.id)

def user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=profile_user)
    user_posts = profile_user.posts.all().order_by('-timestamp')
    user_guesses = profile_user.guesses.all().order_by('-timestamp')
    
    total_points = profile.points
    total_posts = user_posts.count()
    total_guesses = user_guesses.count()
    total_correct_words = sum(len(g.correct_words) for g in user_guesses)
    
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'posts': user_posts,
        'guesses': user_guesses[:20],
        'total_points': total_points,
        'total_posts': total_posts,
        'total_guesses': total_guesses,
        'total_correct_words': total_correct_words,
    }
    return render(request, 'posts/user_profile.html', context)

def leaderboard(request):
    # get users by descending points
    users = User.objects.select_related('profile').order_by('-profile__points').all()
    
    ranked_users = []
    for idx, user in enumerate(users, 1):

        if not hasattr(user, 'profile'):
            Profile.objects.get_or_create(user=user)
        
        ranked_users.append({
            'rank': idx,
            'user': user,
            'points': user.profile.points,
            'post_count': user.posts.count(),
            'guess_count': user.guesses.count(),
        })
    
    user_rank = None
    if request.user.is_authenticated:
        for item in ranked_users:
            if item['user'].id == request.user.id:
                user_rank = item['rank']
                break
    
    context = {
        'users': ranked_users[:50],
        'user_rank': user_rank,
        'total_users': User.objects.count(),
    }
    return render(request, 'posts/leaderboard.html', context)

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('-timestamp')
    
    has_guessed = False
    user_guess = None
    if request.user.is_authenticated:
        user_guess = Guess.objects.filter(author=request.user, post=post).first()
        has_guessed = user_guess is not None
    
    all_guesses = post.guesses.select_related('author').all().order_by('-score_earned')
    
    context = {
        'post': post,
        'has_guessed': has_guessed,
        'user_guess': user_guess,
        'all_guesses': all_guesses,
        'comments': comments,  
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def comment_create(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        symbols = request.POST.get('symbols', '')
        if symbols:
            Comment.objects.create(
                author=request.user,
                post=post,
                symbols=symbols,
            )
            messages.success(request, "Comment added!")
        else:
            messages.error(request, "Please add some symbols to your comment")
    
    return redirect('post_detail', post_id=post.id)


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    
    if request.user == comment.author or request.user.is_superuser:
        comment.delete()
        messages.success(request, "Comment deleted")
    else:
        messages.error(request, "You don't have permission to delete this comment")
    
    return redirect('post_detail', post_id=post_id)

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        symbols = request.POST.get('symbols')
        
        if not symbols:
            messages.error(request, "Please add symbols to explain the prompt")
            return render(request, 'posts/post_edit.html', {'post': post})
        
        post.symbols = symbols
        post.save()
        
        messages.success(request, "Post updated successfully!")
        return redirect('post_detail', post_id=post.id)
    
    return render(request, 'posts/post_edit.html', {'post': post})


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect('post_list')
    
    return render(request, 'posts/post_confirm_delete.html', {'post': post})


@login_required
def admin_post_delete(request, post_id):
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to do that")
        return redirect('post_list')
    
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    messages.success(request, f"Post by {post.author.username} has been deleted")
    return redirect('post_list')