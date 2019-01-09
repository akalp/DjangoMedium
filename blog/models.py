from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from django.db.models import Q

from django.core.paginator import Paginator


class Topic(models.Model):
    name = models.CharField(max_length=200, primary_key=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
        primary_key=True,
    )
    first_name = models.CharField('first name', max_length=30, blank=False)
    last_name = models.CharField('last name', max_length=150, blank=False)
    email = models.EmailField('email address', blank=False, unique=True)

    birthdate = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars', default='avatars/profile-default.png')

    followed_topics = models.ManyToManyField(Topic, related_name='users', blank=True)

    following = models.ManyToManyField('self', related_name='follows', symmetrical=False, blank=True)

    blocked_users = models.ManyToManyField('self', related_name='blocked_by', symmetrical=False, blank=True)

    def recent_posts(self):
        return Post.objects.filter(author=self, published_date__isnull=False).order_by('-published_date')

    def recent_comments(self):
        return Comment.objects.filter(author=self).order_by('-created_date')

    def recent_likes(self):
        return Post.objects.filter(likes__in=[self])

    def followed_posts(self):
        topics = self.followed_topics.all()
        followed_users = self.following.all()
        blocked_users = self.blocked_users.all()
        q_objects = Q()

        if topics.count() >= 1:
            for topic in topics:
                q_objects.add(Q(topics__name__in=[topic]), Q.OR)

        if followed_users.count() >= 1:
            for user in followed_users:
                q_objects.add(Q(author=user), Q.OR)

        if blocked_users.count() >= 1:
            for user in blocked_users:
                q_objects.add(~Q(author=user), Q.AND)

        if q_objects:
            posts = Post.objects.filter(
                q_objects, published_date__isnull=False).distinct().order_by('-published_date')
            return posts
        else:
            return False

    def paginated_followed_posts(self):
        return Paginator(self.followed_posts(), 10)

    def __str__(self):
        return self.username


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE, )
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(
        upload_to='posts', blank=True)

    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    topics = models.ManyToManyField(Topic, related_name='topic_posts')

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="post_likes", symmetrical=False, blank=True)

    bookmarks = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="post_bookmarks", symmetrical=False, blank=True)

    def author_string(self):
        return str(self.author)

    def all_comments(self):
        return self.comments.all().order_by('-created_date')

    def __str__(self):
        return self.title

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def get_absolute_url(self):
        return reverse('blog:post', kwargs={'pk': self.pk})


class Comment(models.Model):
    post = models.ForeignKey(
        Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE, )
    content = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return reverse('post', kwargs={
            'pk': self.pk
        })


class ReportType(models.Model):
    type = models.CharField(max_length=250, blank=False)

    def __str__(self):
        return self.type


class PostReport(models.Model):
    class Meta:
        unique_together = (('user', 'post'),)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='report_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE, related_name='reported_posts', blank=False)

    def __str__(self):
        return str(self.user)+" report "+str(self.post)+" by "+str(self.post.author)+" with "+str(self.report_type)


class UserReport(models.Model):
    class Meta:
        unique_together = (('reporter', 'reported'),)

    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='report_users')
    reported = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE, related_name='reported_users', blank=False)

    def __str__(self):
        return str(self.reporter)+" report "+str(self.reported)+" with "+str(self.report_type)
