from django import template
from blog.models import CustomUser, Post, PostReport, UserReport, Collection
register = template.Library()


@register.filter
def already_followed_user(pk, user):
    author = CustomUser.objects.get(pk=pk)
    return author in user.following.all()


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


@register.filter
def already_bookmarked_post(post_pk, user):
    post = Post.objects.get(pk=post_pk)
    return user in post.bookmarks.all()


@register.filter
def already_blocked_user(pk, user):
    block = CustomUser.objects.get(pk=pk)
    return block in user.blocked_users.all()


@register.filter
def not_reported_user(pk, user):
    if UserReport.objects.filter(reporter=user, reported__pk=pk).count() > 0:
        return False
    return True


@register.filter
def not_reported_post(pk, user):
    if PostReport.objects.filter(user=user, post__pk=pk).count() > 0:
        return False
    return True


@register.filter
def already_bookmarked_collection(collection_pk, user):
    collection = Collection.objects.get(pk=collection_pk)
    return user in collection.bookmarked_by.all()

