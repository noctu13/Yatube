from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User
from .forms import PostForm

def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})

def group_all(request):
    group_list = Group.objects.all()
    paginator = Paginator(group_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group_all.html", {'page': page, 'paginator': paginator})

@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, "new_post.html", {"form": form})

def profile_view(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=profile).order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {"profile": profile, 'page': page, 'paginator': paginator})

def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    queryset = Post.objects.filter(author=profile).order_by("pub_date")
    post_dict = dict(enumerate(queryset))
    try:
        post = post_dict[post_id]
    except KeyError:
        return render(request, "404.html")
    return render(request, "post.html", {"profile": profile, "post": post})

@login_required
def post_edit(request, username, post_id):
    if request.user == get_object_or_404(User, username=username):
        queryset = Post.objects.filter(author=request.user).order_by("pub_date")
        post_dict = dict(enumerate(queryset))
        try:
            post = post_dict[post_id]
        except KeyError:
            return render(request, "404.html")
        #тут может случится потенциальная серверная ошибка?
    else:
        #return render(request, "403.html") было бы логичнее
        return redirect('post', username=username, post_id=post_id)
    #здесь вроде можно использовать вьюху new_post, если передавать post
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm(instance=post)
    return render(request, "edit_post.html", {"form": form})
