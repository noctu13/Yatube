from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm

class PageBack:
    def __init__(self, request, _list):
        if _list:
            self.paginator = Paginator(_list, 10)
            self.page = self.paginator.get_page(request.GET.get('page'))
        else:
            self.paginator = None
            self.page = None

def index(request):
    post_list = Post.objects.all().order_by("-pub_date")
    page_back = PageBack(request, post_list)
    return render(request, 'index.html', {'page': page_back.page, 'paginator': page_back.paginator})

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all().order_by("-pub_date")
    page_back = PageBack(request, post_list)
    return render(request, "group.html", {"group": group, 'page': page_back.page, 'paginator': page_back.paginator})

def group_all(request):
    group_list = Group.objects.all()
    page_back = PageBack(request, group_list)
    return render(request, "group_all.html", {'page': page_back.page, 'paginator': page_back.paginator})

@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, "new_post.html", {"form": form})

def profile_view(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=request.user, author=author).exists() if request.user.is_authenticated else None
    post_list = author.posts.all().order_by("-pub_date")
    page_back = PageBack(request, post_list)
    return render(request, "profile.html", {"author": author, 'following': following, 'page': page_back.page, 'paginator': page_back.paginator})

def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    if author != post.author:
        raise Http404()
    comments = post.comments.all().order_by("-created")
    form = CommentForm(request.POST or None)
    return render(request, "post.html", {"form": form, "post": post, "items": comments})

@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        return redirect('post', username=username, post_id=post_id)
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, "edit_post.html", {"form": form, "post": post})

@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    if author != post.author:
        raise Http404()
    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('post', username=username, post_id=post_id)
    return redirect('post', username=username, post_id=post_id)

@login_required
def follow_index(request):
    follow_list = Follow.objects.filter(user=request.user)
    author_list = User.objects.filter(following__in=follow_list) if follow_list else None
    post_list = Post.objects.filter(author__in=author_list).order_by("-pub_date") if author_list else None
    page_back = PageBack(request, post_list)
    return render(request, "follow.html", {'page': page_back.page, 'paginator': page_back.paginator})

@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username=username)

@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=author)
    follow.delete()
    return redirect('profile', username=username)

def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)

def permission_denied(request, exception):
    return render(request, "misc/403.html", {"path": request.path}, status=403)

def server_error(request):
    return render(request, "misc/500.html", status=500)
