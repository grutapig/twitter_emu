from django.urls import path
from . import views

urlpatterns = [
    path('communities/', views.communities_list, name='api_communities_list'),
    path('communities/<int:community_id>/', views.community_detail, name='api_community_detail'),
    path('tweets/<int:tweet_id>/', views.tweet_detail, name='api_tweet_detail'),
    path('tweets/<int:tweet_id>/replies/', views.tweet_replies, name='api_tweet_replies'),
    path('users/search/', views.users_search, name='api_users_search'),
    path('users/<int:user_id>/', views.user_detail, name='api_user_detail'),
    path('tweets/create/', views.create_tweet, name='api_create_tweet'),
    path('tweets/<int:tweet_id>/delete/', views.delete_tweet, name='api_delete_tweet'),
]