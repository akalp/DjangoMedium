from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Post, Comment, Topic

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Topic)
