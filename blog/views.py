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

from .forms import UserForm, PostForm, UserEditForm, CommentForm, UserReportForm, PostReportForm, CollectionForm, \
    PublicationForm
from .models import Post, Comment, Topic, CustomUser, Collection, Publication, PublicationPost

from django.db import connection

class IndexView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'posts_list'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Main Page'
        return context


class FollowedView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'posts_list'
    paginate_by = 10

    def get_queryset(self):
        posts = self.request.user.followed_posts()
        if posts:
            return posts
        else:
            return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Timeline'
        return context


class BookmarkedPostListView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'posts_list'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(bookmarks__in=[self.request.user]).order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Bookmarked Posts'
        return context


class TopicPostsListView(generic.ListView):
    template_name = 'blog/topic_posts.html'
    context_object_name = 'posts_list'

    def get_queryset(self):
        return Post.objects.filter(topics__name=self.kwargs['topic'], published_date__isnull=False).order_by(
            '-published_date')

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


# User #


class ProfileDetailView(generic.DetailView):
    model = CustomUser
    context_object_name = 'blog_user'
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collections'] = self.object.collections.filter(published_date__isnull=False)
        return context


class FollowerListView(generic.ListView):
    model = CustomUser
    context_object_name = 'users_list'
    template_name = 'blog/userlist.html'

    def get_queryset(self):
        return CustomUser.objects.filter(following__username=self.kwargs['pk'])


class FollowingListView(generic.ListView):
    model = CustomUser
    context_object_name = 'users_list'
    template_name = 'blog/userlist.html'

    def get_queryset(self):
        return CustomUser.objects.filter(follows__username=self.kwargs['pk'])


class BlockedUserListView(generic.ListView):
    model = CustomUser
    context_object_name = 'users_list'
    template_name = 'blog/userlist.html'

    def get_queryset(self):
        print(self.request.user.pk)
        return CustomUser.objects.filter(blocked_by=self.request.user)


def my_profile(request):
    collections = request.user.collections.filter(published_date__isnull=False)
    return render(request, 'blog/profile.html', {'blog_user': request.user, 'collections': collections})


def register_user(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            new_user = user_form.save(commit=False)

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


@login_required
def report_user(request, reported_pk):
    if request.method == 'POST':
        report_form = UserReportForm(data=request.POST)

        if report_form.is_valid():
            report = report_form.save(commit=False)
            report.reporter = request.user
            report.reported = CustomUser.objects.get(pk=reported_pk)
            report.save()
            return HttpResponseRedirect(reverse('blog:profile', kwargs={'pk': reported_pk}))
        else:
            print(report_form.errors)
    else:
        report_form = UserReportForm()

    return render(request, 'blog/report.html', {'report_form': report_form, 'info_title': 'User:',
                                                'info': str(CustomUser.objects.get(pk=reported_pk))})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('blog:index'))
        else:
            messages.error(request, 'username or password not correct')
            return HttpResponseRedirect(reverse('blog:login'))
    else:
        return render(request, 'blog/login.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('blog:index'))


@login_required
def profile_edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(data=request.POST, instance=request.user)
        if 'avatar' in request.FILES:
            user_form.instance.set_image(request.FILES['avatar'])
        user_form.save()

        return HttpResponseRedirect(reverse('blog:me_edit'))
    else:
        user_form = UserEditForm(instance=request.user)
        return render(request, 'blog/profile_edit.html', {
            'user_form': user_form,
        })


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
def follow_user2(request, pk):
    user = request.user

    follow = CustomUser.objects.get(pk=pk)

    user.following.add(follow)
    user.save()
    return redirect('blog:profile', pk=pk)


@login_required
def unfollow_user2(request, pk):
    user = request.user

    follow = CustomUser.objects.get(pk=pk)

    user.following.remove(follow)
    user.save()
    return redirect('blog:profile', pk=pk)


@login_required
def block_user(request, pk):
    user = request.user

    block = CustomUser.objects.get(pk=pk)

    user.blocked_users.add(block)
    user.save()
    return redirect('blog:index')


@login_required
def unblock_user(request, pk):
    user = request.user

    block = CustomUser.objects.get(pk=pk)

    user.blocked_users.remove(block)
    user.save()
    return redirect('blog:index')


# Topic #


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


# Post #

class NewPostView(LoginRequiredMixin, generic.CreateView):
    login_url = '/login/'
    template_name = 'blog/new_post.html'
    form_class = PostForm
    model = Post

    def form_valid(self, form):
        form.instance.author = self.request.user
        post = form.save()
        if 'publication_pk' in self.kwargs.keys():
            PublicationPost(post_id=post.id, publication_id=self.kwargs['publication_pk']).save()
        return HttpResponseRedirect(reverse('blog:post', kwargs={'pk': post.pk}))


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
        context['title'] = self.object.title
        return context


class PostEditView(LoginRequiredMixin, generic.UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post.html'
    template_name = 'blog/new_post.html'
    form_class = PostForm
    model = Post


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return HttpResponseRedirect(reverse('blog:post', kwargs={'pk': pk}))


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


@login_required
def add_bookmark(request, pk):
    post = Post.objects.get(pk=pk)
    post.bookmarks.add(request.user)
    post.save()
    return redirect('blog:post', pk=pk)


@login_required
def remove_bookmark(request, pk):
    post = Post.objects.get(pk=pk)
    post.bookmarks.remove(request.user)
    post.save()
    return redirect('blog:post', pk=pk)


@login_required
def report_post(request, reported_pk):
    if request.method == 'POST':
        report_form = PostReportForm(data=request.POST)

        if report_form.is_valid():
            report = report_form.save(commit=False)
            report.user = request.user
            report.post = Post.objects.get(pk=reported_pk)
            report.save()
            return HttpResponseRedirect(reverse('blog:post', kwargs={'pk': reported_pk}))
        else:
            print(report_form.errors)
    else:
        report_form = UserReportForm()

    post = Post.objects.get(pk=reported_pk)
    author = post.author
    return render(request, 'blog/report.html',
                  {'report_form': report_form, 'info_title': 'Post:', 'info': str(post) + " by " + str(author)})


@login_required
def add_comment(request, pk):
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = Post.objects.get(pk=pk)
            comment.author = request.user
            comment.save()
    return HttpResponseRedirect(reverse('blog:post', kwargs={'pk': pk}))


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('blog:post', pk=post_pk)


# def new_post(request):
#     if request.method == 'POST':
#         post_form = PostForm(data=request.POST)
#         if post_form.is_valid():
#             post = post_form.save(commit=False)
#             post.author = request.user
#             post.save()
#
#             if 'image' in request.FILES:
#                 post.image = request.FILES['image']
#                 post.save()
#
#     else:
#         post_form = PostForm()
#
#     return render(request, 'blog/new_post.html', {
#         'form': post_form,
#     })


# Collection #


class DraftCollectionsListView(generic.ListView):
    template_name = 'blog/collection_list.html'
    context_object_name = 'collection_list'

    def get_queryset(self):
        return Collection.objects.filter(published_date=None, creator=self.request.user)


class SelectCollectionsListView(generic.ListView):
    template_name = 'blog/select_collection_list.html'
    context_object_name = 'collection_list'

    def get_queryset(self):
        return Collection.objects.filter(published_date=None, creator=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.kwargs['post_pk']
        return context


class BookmarkedCollectionsListView(generic.ListView):
    template_name = 'blog/collection_list.html'
    context_object_name = 'collection_list'

    def get_queryset(self):
        return Collection.objects.filter(bookmarked_by__in=[self.request.user])


class CollectionsListView(generic.ListView):
    template_name = 'blog/collection_list.html'
    context_object_name = 'collection_list'

    def get_queryset(self):
        return Collection.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')


class CollectionDetailView(generic.DetailView):
    model = Collection
    template_name = 'blog/collection.html'


class CollectionCreateView(LoginRequiredMixin, generic.CreateView):
    login_url = '/login/'
    redirect_field_name = 'blog/collection.html'
    template_name = 'blog/new_collection.html'
    form_class = CollectionForm
    model = Collection

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class CollectionEditView(LoginRequiredMixin, generic.UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/collection.html'
    template_name = 'blog/new_collection.html'
    form_class = CollectionForm
    model = Collection


class CollectionDeleteView(LoginRequiredMixin, generic.DeleteView):
    login_url = '/login/'
    model = Collection
    success_url = reverse_lazy('blog:index')


@login_required
def add_bookmark_collection(request, pk):
    collection = Collection.objects.get(pk=pk)
    collection.bookmarked_by.add(request.user)
    collection.save()
    return redirect('blog:collection', pk=pk)


@login_required
def remove_bookmark_collection(request, pk):
    collection = Collection.objects.get(pk=pk)
    collection.bookmarked_by.remove(request.user)
    collection.save()
    return redirect('blog:collection', pk=pk)


@login_required
def add_post_to_collection(request, post_pk, collection_pk):
    collection = Collection.objects.get(pk=collection_pk)
    collection.posts.add(Post.objects.get(pk=post_pk))
    collection.save()
    return redirect('blog:collection', pk=collection_pk)


@login_required
def remove_post_from_collection(request, post_pk, collection_pk):
    collection = Collection.objects.get(pk=collection_pk)
    collection.posts.remove(Post.objects.get(pk=post_pk))
    collection.save()
    return redirect('blog:collection', pk=collection_pk)


@login_required
def collection_publish(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    collection.publish()
    return HttpResponseRedirect(reverse('blog:collection', kwargs={'pk': pk}))


# Publication #

class PublicationsListView(generic.ListView):
    template_name = 'blog/publication_list.html'
    context_object_name = 'publication_list'

    def get_queryset(self):
        return Publication.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')


class PublicationDetailView(generic.DetailView):
    model = Publication
    template_name = 'blog/publication.html'


class PublicationCreateView(LoginRequiredMixin, generic.CreateView):
    login_url = '/login/'
    redirect_field_name = 'blog/publication.html'
    template_name = 'blog/new_publication.html'
    form_class = PublicationForm
    model = Publication

    def form_valid(self, form):
        form.instance.creator = self.request.user
        pub = form.save()
        pub.authors.add(self.request.user)
        return super().form_valid(form)


class PublicationDeleteView(LoginRequiredMixin, generic.DeleteView):
    login_url = '/login/'
    model = Publication
    success_url = reverse_lazy('blog:index')


class PublicationChangeView(LoginRequiredMixin, generic.UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/publication.html'
    template_name = 'blog/new_publication.html'
    form_class = PublicationForm
    model = Publication


class UserPublicationsListView(generic.ListView):
    template_name = 'blog/publication_list.html'
    context_object_name = 'publication_list'

    def get_queryset(self):
        return self.request.user.publications.all()


class FollowedPublicationsListView(generic.ListView):
    template_name = 'blog/publication_list.html'
    context_object_name = 'publication_list'

    def get_queryset(self):
        return self.request.user.followed_publications.all()


class PublicationAuthorListView(generic.ListView):
    # login_url = '/login/'
    template_name = 'blog/author_list.html'
    context_object_name = 'author_list'

    def get_queryset(self):
        return Publication.objects.get(pk=self.kwargs['publication_pk']).authors.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['publication_pk'] = self.kwargs['publication_pk']
        context['creator_pk'] = Publication.objects.get(pk=context['publication_pk']).creator.username
        return context


@login_required
def follow_publication(request, publication_pk):
    user = request.user

    follow = Publication.objects.get(pk=publication_pk)

    user.followed_publications.add(follow)
    user.save()
    return redirect('blog:publication', pk=publication_pk)


@login_required
def unfollow_publication(request, publication_pk):
    user = request.user

    follow = Publication.objects.get(pk=publication_pk)

    user.followed_publications.remove(follow)
    user.save()
    return redirect('blog:publication', pk=publication_pk)


@login_required
def publication_add_author(request, publication_pk):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = CustomUser.objects.get(pk=username)
            Publication.objects.get(pk=publication_pk).authors.add(user)
            messages.success(request, "{} is added".format(username))
            return HttpResponseRedirect(reverse('blog:add_author', kwargs={'publication_pk': publication_pk}))
        except:
            messages.error(request, '{} is not found'.format(username))
            return HttpResponseRedirect(reverse('blog:add_author', kwargs={'publication_pk': publication_pk}))
    else:
        return render(request, 'blog/addauthor.html', {'publication_pk': publication_pk})


@login_required
def publication_remove_author(request, publication_pk, user_pk):
    user = CustomUser.objects.get(pk=user_pk)
    publication = Publication.objects.get(pk=publication_pk)

    publication.authors.remove(user)
    publication.save()
    if request.user == publication.creator:
        return redirect('blog:author_list', publication_pk=publication_pk)
    return redirect('blog:publication', pk=publication_pk)


class PublicationFollowerListView(generic.ListView):
    model = CustomUser
    context_object_name = 'users_list'
    template_name = 'blog/userlist.html'

    def get_queryset(self):
        return CustomUser.objects.filter(followed_publications__in=[self.kwargs['pk']])


# Report #

def admin_report_view(request):
    report = {}
    with connection.cursor() as cursor:
        cursor.execute("SELECT topics.name, count(post_id) FROM blog_topic AS topics LEFT JOIN blog_post_topics AS posts ON topics.name=posts.topic_id GROUP BY topics.name ORDER BY count(posts.post_id) DESC")
        result = cursor.fetchall()
        report['topics_report'] = dict(result)

        cursor.execute("SELECT count(*) FROM blog_publication")
        report['publication_count'] = cursor.fetchone()[0]

        cursor.execute("SELECT avg(count) FROM publicationposts")
        report['avg_post_of_publications'] = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM blog_collection")
        report['collection_count'] = cursor.fetchone()[0]

        cursor.execute("SELECT avg(count) FROM (SELECT count(post_id) as count FROM blog_collection, blog_collection_posts WHERE blog_collection.id=blog_collection_posts.collection_id GROUP BY blog_collection.id) ta")
        report['avg_post_of_collections'] = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM blog_customuser")
        report['user_count'] = cursor.fetchone()[0]

        cursor.execute(
            "SELECT avg(count) FROM (SELECT count(id) as count FROM blog_customuser, blog_post WHERE blog_customuser.username=blog_post.author_id GROUP BY blog_post.author_id) ta")
        report['avg_post_of_users'] = cursor.fetchone()[0]

        cursor.execute("SELECT blog_customuser_following.from_customuser_id as username, count(to_customuser_id) as follows FROM  blog_customuser_following group by blog_customuser_following.from_customuser_id order by follows desc;")
        row = cursor.fetchone()
        if row is not None:
            report['who_follows_most_user'] = row[0]
            report['follows'] = row[1]
        else:
            report['who_follows_most_user'] = "-"
            report['follows'] = "-"

        cursor.execute(
            "SELECT blog_customuser_following.to_customuser_id as username, count(from_customuser_id) as follows FROM  blog_customuser_following group by blog_customuser_following.to_customuser_id order by follows desc;")
        row = cursor.fetchone()
        if row is not None:
            report['who_following_by_most_user'] = row[0]
            report['following'] = row[1]
        else:
            report['who_following_by_most_user'] = "-"
            report['following'] = "-"

        cursor.execute("SELECT blog_reporttype.type, count(blog_userreport.reported_id)  FROM blog_reporttype, blog_userreport WHERE blog_reporttype.id=blog_userreport.report_type_id GROUP BY blog_reporttype.id")
        report['user_reporttype'] = dict(cursor.fetchall())

        cursor.execute("SELECT blog_reporttype.type, count(blog_postreport.post_id)  FROM blog_reporttype, blog_postreport WHERE blog_reporttype.id=blog_postreport.report_type_id GROUP BY blog_reporttype.id")
        report['post_reporttype'] = dict(cursor.fetchall())

    return render(request, 'blog/admin_report.html', report)


# Topic

class TopicListView(generic.ListView):
    model = Topic
    template_name = 'topic_list.html'
    context_object_name = 'topics'


class FollowedTopicsListView(generic.ListView):
    template_name = 'blog/topic_list.html'
    context_object_name = 'topics'

    def get_queryset(self):
        return self.request.user.followed_topics.all()
