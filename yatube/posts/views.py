from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Это главная страница проекта Yatube'
    context = {
        'title': title,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = group.title
    context = {
        'title': title,
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    template = 'posts/profile.html'
    post_list = author.posts.all()
    count = post_list.count()
    sub_count = author.following.all().count()
    paginator = Paginator(post_list, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    sub = True
    try:
        request.user.follower.get(author=author)
        following = True
    except:
        following = False

    if author == request.user:
        sub = False

        following = True

    title = f'Профайл пользователя {username}'

    context = {
        'title': title,
        'page_obj': page_obj,
        'count': count,
        'author': author,
        'following': following,
        'sub': sub,
        'sub_count': sub_count
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    count = post.author.posts.all().count()
    sub_count = post.author.following.all().count()
    form = CommentForm(request.POST or None)
    comments_list = post.comments.all()
    title = str(post)
    context = {
        'title': title,
        'post': post,
        'count': count,
        'form': form,
        'comments': comments_list,
        'sub_count': sub_count
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    title = 'Добавить запись'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method != 'POST':
        context = {
            'title': title,
            'form': form
        }
        return render(request, template, context)
    if not form.is_valid():
        return render(request, template, {'form': form})

    form = form.save(commit=False)
    form.author = request.user
    form.save()
    return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    posts = get_object_or_404(Post, pk=post_id)
    template = 'posts/create_post.html'

    if posts.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    title = 'Редактировать запись'
    is_edit = True
    form = PostForm(
        request.POST or None,
        instance=posts,
        files=request.FILES or None
    )
    if request.method != 'POST':
        context = {
            'title': title,
            'form': form,
            'is_edit': is_edit,
            'post': posts,
        }
        return render(request, template, context)
    if not form.is_valid():
        return render(request, template, {'form': form})
    form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    followers = request.user.follower.all()
    template = 'posts/follow.html'
    post_list = Post.objects.none()

    for follower in followers:
        post = Post.objects.filter(author=follower.author)
        post_list = post_list | post

    paginator = Paginator(post_list, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Это главная страница проекта Yatube'
    context = {
        'title': title,
        'page_obj': page_obj,
    }

    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect('posts:profile', username=username)
    elif author.following.filter(user=request.user):
        return redirect('posts:profile', username=username)
    else:
        Follow.objects.create(user=request.user, author=author)
        return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    author.following.get(user=request.user).delete()
    return redirect('posts:profile', username=username)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect('posts:profile', username=request.user)
