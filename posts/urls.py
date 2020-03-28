from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("group/<str:slug>", views.group_posts, name="group"),
    path("groups", views.group_all, name="group_all"),
    path("new", views.new_post, name="new_post"),
]

user_patterns = [
    path("<username>/", views.profile_view, name="profile"),
    path("<username>/<int:post_id>/", views.post_view, name="post"),
    path("<username>/<int:post_id>/edit", views.post_edit, name="post_edit"),
]
