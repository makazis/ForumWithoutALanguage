from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q, F
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import Post, Tag, Guess, Comment, Profile

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
    return render(request, 'posts/post_list.html', {'page_obj': page_obj,'posts':posts})

@login_required
def post_create(request):
    all_tags = Tag.objects.all()
    
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        symbols = request.POST.get('symbols')
        
        if not prompt or not symbols:
            messages.error(request, "Please fill in all fields")
            return render(request, 'posts/post_create.html', {'all_tags': all_tags})
        post = Post.objects.create(
            author=request.user,
            prompt=prompt,
            symbols="".join(symbols.split(",")),
            guess_count=0
        )
        messages.success(request, "Post created successfully! Others will now try to guess your meaning.")
        return redirect('post_detail', post_id=post.id)
    
    return render(request, 'posts/post_create.html', {'all_tags': all_tags})

@login_required
def submit_guess(request, post_id):
    """Process a user's tag guess"""
    post = get_object_or_404(Post, id=post_id)
    
    # Check if already guessed
    if Guess.objects.filter(user=request.user, post=post).exists():
        messages.warning(request, "You already guessed on this post!")
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        guessed_tag_ids = request.POST.getlist('guessed_tags')
        guesser_profile, _ = Profile.objects.get_or_create(user=request.user)
        author_profile, _ = Profile.objects.get_or_create(user=post.author)
        
        if is_correct:
            # 15 points to guesser, 10 to creator
            guesser_profile.points += 15
            guesser_profile.save()
            
            author_profile.points += 10
            author_profile.save()
        if not guessed_tag_ids:
            messages.error(request, "Please select at least one tag")
            return redirect('post_detail', post_id=post.id)
        
        # Create the guess record
        guess = Guess.objects.create(
            user=request.user,
            post=post,
            is_correct=False,  # We'll calculate this later
        )
        guess.guessed_tags.set(guessed_tag_ids)
        
        messages.success(request, "Guess submitted!")
        
    return redirect('post_detail', post_id=post.id)


# posts/views.py - Updated user_profile view
def user_profile(request, user_id):
    """Display user profile with their posts and stats"""
    profile_user = get_object_or_404(User, id=user_id)
    user_posts = profile_user.posts.all().order_by('-timestamp')
    
    # Get or create profile (safety check)
    profile, created = Profile.objects.get_or_create(user=profile_user)
    
    # Get user's stats
    total_posts = user_posts.count()
    total_guesses_made = profile_user.guesses.count()
    total_points = profile.points
    
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'posts': user_posts,
        'total_posts': total_posts,
        'total_guesses': total_guesses_made,
        'total_points': total_points,
    }
    return render(request, 'posts/user_profile.html', context)
# Add this function for leaderboard
# posts/views.py - Updated leaderboard view
def leaderboard(request):
    """Display global leaderboard sorted by points"""
    # Get all users with their profiles, ordered by points descending
    users = User.objects.select_related('profile').order_by('-profile__points').all()
    
    # Add rank to each user
    ranked_users = []
    for idx, user in enumerate(users, 1):
        # Ensure profile exists
        if not hasattr(user, 'profile'):
            Profile.objects.get_or_create(user=user)
        
        ranked_users.append({
            'rank': idx,
            'user': user,
            'points': user.profile.points,
            'post_count': user.posts.count(),
            'guess_count': user.guesses.count(),
        })
    
    # Get current user's rank (if authenticated)
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

# Update your post_detail view to include the guessing logic
def post_detail(request, post_id):
    """Display a single post with its symbols and guessing form"""
    post = get_object_or_404(Post, id=post_id)
    all_tags = Tag.objects.all()
    
    # Check if current user already guessed this post
    has_guessed = False
    user_guess = None
    if request.user.is_authenticated:
        user_guess = Guess.objects.filter(author=request.user, post=post).first()
        has_guessed = user_guess is not None
    
    # Get all guesses for this post (for display)
    all_guesses = post.guesses.select_related('author').prefetch_related('guessed_tags').all()
    
    # Get comments (for later - symbol-only comments)
    comments = post.comments.all().order_by('timestamp') if hasattr(post, 'comments') else []
    
    context = {
        'post': post,
        'all_tags': all_tags,
        'has_guessed': has_guessed,
        'user_guess': user_guess,
        'all_guesses': all_guesses,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


# Add/Update the submit_guess view with full point calculation
@login_required
def submit_guess(request, post_id):
    """Process a user's tag guess and award points if correct"""
    post = get_object_or_404(Post, id=post_id)
    
    # Check if already guessed
    if Guess.objects.filter(user=request.user, post=post).exists():
        messages.warning(request, "You already guessed on this post!")
        return redirect('post_detail', post_id=post.id)
    
    # Don't allow guessing on your own post
    if request.user == post.author:
        messages.error(request, "You cannot guess on your own post!")
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        guessed_tag_ids = [int(id) for id in request.POST.getlist('guessed_tags')]
        
        if not guessed_tag_ids:
            messages.error(request, "Please select at least one tag")
            return redirect('post_detail', post_id=post.id)
        
        # Get intended tags as set of IDs
        intended_ids = set(post.intended_tags.values_list('id', flat=True))
        guessed_set = set(guessed_tag_ids)
        
        # Calculate correctness (exact match required for full points)
        is_correct = (intended_ids == guessed_set)
        
        # Calculate partial points (optional: 5 points if at least one correct)
        has_correct_tag = len(intended_ids.intersection(guessed_set)) > 0
        partial_points = has_correct_tag and not is_correct
        
        # Create the guess record
        guess = Guess.objects.create(
            user=request.user,
            post=post,
            is_correct=is_correct,
        )
        guess.guessed_tags.set(guessed_tag_ids)
        
        # Award points
        points_awarded = 0
        if is_correct:
            # 15 points to guesser, 10 to creator
            request.user.profile.points += 15
            request.user.profile.save()
            
            post.author.profile.points += 10
            post.author.profile.save()
            
            post.points_awarded = True
            post.save()
            
            points_awarded = 15
            messages.success(
                request, 
                f"🎉 CORRECT! You earned 15 points! {post.author.username} earned 10 points!"
            )
        elif partial_points:
            # 5 points for at least one correct tag
            request.user.profile.points += 5
            request.user.profile.save()
            points_awarded = 5
            messages.info(
                request,
                "👍 Partial match! You got at least one tag right. +5 points!"
            )
        else:
            messages.info(request, "❌ No matches. Try another post!")
        
        # Store points awarded in session for display
        request.session['last_points'] = points_awarded
        
    return redirect('post_detail', post_id=post.id)

# posts/views.py - Add these comment views

@login_required
def comment_create(request, post_id):
    """Add a symbol-only comment to a post"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        symbol_sequence = request.POST.get('symbol_sequence')
        if symbol_sequence:
            Comment.objects.create(
                author=request.user,
                post=post,
                symbol_sequence=symbol_sequence,
            )
            messages.success(request, "Comment added!")
    
    return redirect('post_detail', post_id=post.id)

@login_required
def comment_delete(request, comment_id):
    """Delete a comment (author or admin only)"""
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    
    if request.user == comment.author or request.user.is_superuser:
        comment.delete()
        messages.success(request, "Comment deleted")
    else:
        messages.error(request, "You don't have permission to delete this comment")
    
    return redirect('post_detail', post_id=post_id)