from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages

from itertools import chain
import re

from .forms import (UserForm, PostForm, UserEditForm, CommentForm)
from .models import Post, Comment, Topic, CustomUser


class IndexView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'posts_list'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')


class FollowedView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.followed_post().order_by('-published_date')


class TopicPostsListView(generic.ListView):
    template_name = 'blog/topic_posts.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        return Post.objects.filter(topics__in=Topic.objects.get(pk=self.kwargs['topic']))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topic'] = self.kwargs['topic']
        return context


class DraftsListView(generic.ListView):
    template_name = 'blog/drafts.html'
    context_object_name = 'posts_list'

    def get_queryset(self):
        return Post.objects.filter(published_date=None, author=self.request.user)


class SearchListView(generic.ListView):
    template_name = 'blog/search.html'
    context_object_name = 'posts_list'
    paginate_by = 10

    def get_queryset(self):
        search = self.request.GET.get('search')
        return Post.objects.filter(Q(published_date__lte=timezone.now()),
                                   Q(title__contains=search) | Q(content__contains=search)).order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search')
        return context


class NewPostView(LoginRequiredMixin, generic.CreateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post.html'
    template_name = 'blog/new_post.html'
    form_class = PostForm
    model = Post

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, generic.DeleteView):
    login_url = '/login/'
    model = Post
    success_url = reverse_lazy('blog:index')


class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'blog/post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context


class ProfileDetailView(generic.DetailView):
    model = CustomUser
    context_object_name = 'blog_user'
    template_name = 'blog/profile.html'


class PostEditView(LoginRequiredMixin, generic.UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post.html'
    template_name = 'blog/new_post.html'
    form_class = PostForm
    model = Post


def add_comment(request, pk):
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = Post.objects.get(pk=pk)
            comment.author = request.user
            comment.save()
    return HttpResponseRedirect(reverse('blog:post', kwargs={'pk': pk}))


def my_profile(request):
    return render(request, 'blog/profile.html', {'blog_user': request.user})


def register_user(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(new_user.password)

            if 'avatar' in request.FILES:
                new_user.avatar = request.FILES['avatar']

            new_user.save()
            registered = True
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()
    return render(request, 'blog/registration.html', {
        'user_form': user_form,
        'registered': registered
    })


def new_post(request):

    if request.method == 'POST':
        post_form = PostForm(data=request.POST)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()

            if 'image' in request.FILES:

                post.image = request.FILES['image']
                post.save()

    else:
        post_form = PostForm()

    return render(request, 'blog/new_post.html', {
        'form': post_form,
    })


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('blog:index'))
        else:
            messages.error(request,'username or password not correct')
            return HttpResponseRedirect(reverse('blog:login'))
    else:
        return render(request, 'blog/login.html')


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return HttpResponseRedirect(reverse('blog:post', kwargs={'pk': pk}))


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('blog:index'))


@login_required
def profile_edit(request):

    if request.method == 'POST':
        user_form = UserEditForm(data=request.POST, instance=request.user)
        if 'avatar' in request.FILES:
            user_form.avatar = request.FILES['avatar']
        user_form.save()

        return HttpResponseRedirect(reverse('blog:me_edit'))
    else:
        user_form = UserEditForm(instance=request.user)
        return render(request, 'blog/profile_edit.html', {
            'user_form': user_form,
        })


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('blog:post', pk=post_pk)


@login_required
def follow_user(request, author_pk, post_pk):
    user = request.user

    follow = CustomUser.objects.get(pk=author_pk)

    user.following.add(follow)
    user.save()
    return redirect('blog:post', pk=post_pk)


@login_required
def unfollow_user(request, author_pk, post_pk):
    user = request.user

    follow = CustomUser.objects.get(pk=author_pk)

    user.following.remove(follow)
    user.save()
    return redirect('blog:post', pk=post_pk)


@login_required
def follow_topic(request, topic):
    user = request.user
    user.followed_topics.add(Topic.objects.get(pk=topic))
    user.save()
    return redirect('blog:topics', topic=topic)


@login_required
def unfollow_topic(request, topic):
    user = request.user
    user.followed_topics.remove(Topic.objects.get(pk=topic))
    user.save()
    return redirect('blog:topics', topic=topic)


@login_required
def add_like(request, pk):
    post = Post.objects.get(pk=pk)
    post.likes.add(request.user)
    post.save()
    return redirect('blog:post', pk=pk)


@login_required
def remove_like(request, pk):
    post = Post.objects.get(pk=pk)
    post.likes.remove(request.user)
    post.save()
    return redirect('blog:post', pk=pk)
