from django.urls import path
from blog import views

app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('following', views.FollowedView.as_view(), name='following'),
    path('register/', views.register_user, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('new/', views.NewPostView.as_view(), name='new'),
    # path('new2/', views.new_post, name='new2'),
    path('follow/<author_pk>/<int:post_pk>',
         views.follow_user, name='follow_user'),
    path('unfollow/<author_pk>/<int:post_pk>',
         views.unfollow_user, name='unfollow_user'),
    path('follow/topic/<topic>', views.follow_topic, name='follow_topic'),
    path('unfollow/topic/<topic>', views.unfollow_topic, name='unfollow_topic'),

    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post'),
    path('search/', views.SearchListView.as_view(), name='search'),
    path('post/<int:pk>/edit/', views.PostEditView.as_view(), name='post_edit'),
    path('post/<int:pk>/like/', views.add_like, name='add_like'),
    path('post/<int:pk>/remove_like/', views.remove_like, name='remove_like'),
    path('post/<int:pk>/add_bookmark/', views.add_bookmark, name='add_bookmark'),
    path('post/<int:pk>/remove_bookmark/', views.remove_bookmark, name='remove_bookmark'),
    path('user/<pk>/', views.ProfileDetailView.as_view(), name='profile'),

    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('topics/<topic>', views.TopicPostsListView.as_view(), name='topics'),

    path('post/<int:pk>/comment/delete',
         views.delete_comment, name='delete_comment'),
    path('post/<int:pk>/publish/', views.post_publish, name='post_publish'),

    path('me/edit/', views.profile_edit, name='me_edit'),
    path('me/drafts/', views.DraftsListView.as_view(), name='drafts'),
    path('me/bookmarked/', views.BookmarkedPostListView.as_view(), name='bookmarked'),

    path('me/', views.my_profile, name='me'),



]