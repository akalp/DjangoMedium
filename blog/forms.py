from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser, Post, Comment, UserReport, PostReport, Collection, Publication, ReportType

from datetime import datetime


class UserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2',
                  'email', 'first_name', 'last_name',
                  'birthdate', 'avatar')

        widgets = {
            'birthdate': forms.SelectDateWidget(years=range(1919, datetime.now().year + 1))
        }


class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email',
                  'first_name', 'last_name',
                  'avatar', 'birthdate')

        widgets = {
            'birthdate': forms.SelectDateWidget(years=range(1919, datetime.now().year + 1))
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'topics', 'content', 'image')

        widgets = {
            'title': forms.Textarea(attrs={'class': 'post-title-input', 'placeholder': 'Title'}),
            'content': forms.Textarea(),
            'topics': forms.SelectMultiple(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['content'].label = "Write a comment:"


class UserReportForm(forms.ModelForm):
    class Meta:
        model = UserReport
        fields = ('report_type',)


class PostReportForm(forms.ModelForm):
    class Meta:
        model = PostReport
        fields = ('report_type',)


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ('image', 'title', 'info',)

        widgets = {
            'title': forms.Textarea(attrs={'class': 'post-title-input', 'placeholder': 'Title'}),
            'info': forms.TextInput(),
        }


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ('image', 'name', 'info',)

        widgets = {
            'name': forms.Textarea(attrs={'class': 'post-title-input', 'placeholder': 'Title'}),
            'info': forms.TextInput(),
        }


class ReportTypeForm(forms.ModelForm):
    class Meta:
        model = ReportType
        fields = ('type',)


class AdminPostReportForm(forms.ModelForm):
    class Meta:
        model = PostReport
        fields = ('user', 'post', 'report_type',)


class AdminUserReportForm(forms.ModelForm):
    class Meta:
        model = UserReport
        fields = ('reporter', 'reported', 'report_type',)
