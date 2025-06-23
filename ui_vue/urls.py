from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('community/<int:community_id>/', views.community_detail, name='community_detail'),
    path('tweet/<int:tweet_id>/', views.tweet_detail, name='tweet_detail'),
    path('user/<int:user_id>/', views.user_profile, name='user_profile'),
]