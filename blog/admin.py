from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Post, Comment, Topic, ReportType, UserReport, PostReport, Collection, PublicationPost, Publication
from .forms import ReportTypeForm, AdminPostReportForm, AdminUserReportForm


class report_type_admin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.form = ReportTypeForm
        return super(report_type_admin, self).get_form(request, obj, **kwargs)


class post_report_admin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.form = AdminPostReportForm
        return super(post_report_admin, self).get_form(request, obj, **kwargs)


class user_report_admin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.form = AdminUserReportForm
        return super(user_report_admin, self).get_form(request, obj, **kwargs)


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Topic)
admin.site.register(ReportType, report_type_admin)
admin.site.register(UserReport, user_report_admin)
admin.site.register(PostReport, post_report_admin)
admin.site.register(Collection)
admin.site.register(Publication)
admin.site.register(PublicationPost)
