from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Post, Comment, Topic, ReportType, UserReport, PostReport, Collection

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Topic)
admin.site.register(ReportType)
admin.site.register(UserReport)
admin.site.register(PostReport)
admin.site.register(Collection)
