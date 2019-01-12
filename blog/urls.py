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

    path('follow/<author_pk>/<int:post_pk>', views.follow_user, name='follow_user'),
    path('unfollow/<author_pk>/<int:post_pk>', views.unfollow_user, name='unfollow_user'),
    path('follow/<pk>/', views.follow_user2, name='follow_user2'),
    path('unfollow/<pk>/', views.unfollow_user2, name='unfollow_user2'),

    path('block/<pk>/', views.block_user, name='block_user'),
    path('unblock/<pk>/', views.unblock_user, name='unblock_user'),

    path('report_user/<reported_pk>/', views.report_user, name='report_user'),
    path('report_post/<int:reported_pk>/', views.report_post, name='report_post'),

    path('follow/topic/<topic>/', views.follow_topic, name='follow_topic'),
    path('unfollow/topic/<topic>/', views.unfollow_topic, name='unfollow_topic'),

    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post'),
    path('search/', views.SearchListView.as_view(), name='search'),
    path('post/<int:pk>/edit/', views.PostEditView.as_view(), name='post_edit'),
    path('post/<int:pk>/like/', views.add_like, name='add_like'),
    path('post/<int:pk>/remove_like/', views.remove_like, name='remove_like'),
    path('post/<int:pk>/add_bookmark/', views.add_bookmark, name='add_bookmark'),
    path('post/<int:pk>/remove_bookmark/', views.remove_bookmark, name='remove_bookmark'),

    path('user/<pk>/', views.ProfileDetailView.as_view(), name='profile'),

    path('user/<pk>/followers/', views.FollowerListView.as_view(), name='followers'),
    path('user/<pk>/follows/', views.FollowingListView.as_view(), name='follows'),

    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('topics/<topic>', views.TopicPostsListView.as_view(), name='topics'),

    path('post/<int:pk>/comment/delete',
         views.delete_comment, name='delete_comment'),
    path('post/<int:pk>/publish/', views.post_publish, name='post_publish'),

    path('me/edit/', views.profile_edit, name='me_edit'),
    path('me/drafts/', views.DraftsListView.as_view(), name='drafts'),
    path('me/bookmarked/', views.BookmarkedPostListView.as_view(), name='bookmarked'),
    path('me/blocked/', views.BlockedUserListView.as_view(), name='blockedlist'),

    path('me/', views.my_profile, name='me'),

    path('me/draft_collections/', views.DraftCollectionsListView.as_view(), name='draft_collections'),
    path('me/bookmarked_collections/', views.BookmarkedCollectionsListView.as_view(), name='bookmarked_collections'),

    path('collections/', views.CollectionsListView.as_view(), name='collections'),
    path('collections/<int:pk>/', views.CollectionDetailView.as_view(), name='collection'),
    path('collections/<int:pk>/add_bookmark/', views.add_bookmark_collection, name='add_bookmark_collection'),
    path('collections/<int:pk>/remove_bookmark/', views.remove_bookmark_collection, name='remove_bookmark_collection'),
    path('collections/<int:pk>/edit/', views.CollectionEditView.as_view(), name='collection_edit'),
    path('collections/<int:pk>/delete/', views.CollectionDeleteView.as_view(), name='collection_delete'),
    path('collections/<int:pk>/publish/', views.collection_publish, name='collection_publish'),

    path('add_to_collection/<int:post_pk>/<int:collection_pk>', views.add_post_to_collection, name='add_to_collection'),
    path('select_collection/<int:post_pk>/', views.SelectCollectionsListView.as_view(), name='select_collection'),
    path('remove_from_collection/<int:post_pk>/<int:collection_pk>', views.remove_post_from_collection, name='remove_from_collection'),

    path('collections/new/', views.CollectionCreateView.as_view(), name='new_collection'),

    path('publications/', views.PublicationsListView.as_view(), name='publications'),
    path('publication/<int:pk>/', views.PublicationDetailView.as_view(), name='publication'),
    path('publication/<int:publication_pk>/follow/', views.follow_publication, name='follow_publication'),
    path('publication/<int:publication_pk>/unfollow/', views.unfollow_publication, name='unfollow_publication'),
    path('publication/<int:pk>/edit/', views.PublicationChangeView.as_view(), name='edit_publication'),
    path('publication/<int:pk>/delete/', views.PublicationDeleteView.as_view(), name='delete_publication'),
    path('publications/new/', views.PublicationCreateView.as_view(), name='new_publication'),

    path('publication/<int:publication_pk>/new', views.NewPostView.as_view(), name='collection_new_post'),

    path('user/<pk>/publications/', views.UserPublicationsListView.as_view(), name='user_publications'),
    path('me/followed_publications/', views.FollowedPublicationsListView.as_view(), name='followed_publications'),

    path('publication/<int:publication_pk>/add_author/', views.publicationaddauthor, name='add_author'),
    path('publication/<int:publication_pk>/leave_author/<user_pk>', views.publicationremoveauthor, name='remove_author'),

    path('publication/<int:publication_pk>/authors', views.PublicationAuthorListView.as_view(), name='author_list'),
]
