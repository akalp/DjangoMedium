from django import template
from blog.models import CustomUser, Post
register = template.Library()


@register.filter
def already_followed_user(author_pk, user):
    author = CustomUser.objects.get(pk=author_pk)
    return author in user.profile.following.all()


@register.filter
def already_followed_topic(topic, user):
    for followed in user.followed_topics.all():
        if str(topic) == str(followed):
            return True
    return False


@register.filter
def already_liked(post_pk, user):
    post = Post.objects.get(pk=post_pk)
    return user in post.likes.all()
