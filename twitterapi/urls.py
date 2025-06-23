from django.urls import path
from . import views

urlpatterns = [
    path('twitter/community/tweets/', views.CommunityTweetsListView.as_view(), name='community_tweets'),
    path('twitter/user/last_tweets/', views.UserLastTweetsListView.as_view(), name='user_last_tweets'),
    path('twitter/tweet/replies/', views.TweetRepliesListView.as_view(), name='tweet_replies'),
    path('twitter/user/followers/', views.UserFollowersListView.as_view(), name='user_followers'),
    path('twitter/user/followings/', views.UserFollowingsListView.as_view(), name='user_followings'),
]