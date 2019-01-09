from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser, Post, Comment

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


class UserEditForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('password', 'email',
                  'first_name', 'last_name',
                  'avatar', 'birthdate')


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
