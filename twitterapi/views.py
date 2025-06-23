from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import User, Community, Tweet
from .serializers import TweetSerializer, FollowerSerializer
from .pagination import TwitterCursorPagination, TwitterFollowersPagination, TwitterUserTweetsPagination


class CommunityTweetsListView(generics.ListAPIView):
    serializer_class = TweetSerializer
    pagination_class = TwitterCursorPagination
    
    def get_queryset(self):
        community_id = self.request.query_params.get('community_id')
        if not community_id:
            return Tweet.objects.none()
        
        community = get_object_or_404(Community, twitter_id=community_id)
        return Tweet.objects.filter(community=community)
    
    def list(self, request, *args, **kwargs):
        community_id = request.query_params.get('community_id')
        if not community_id:
            return Response({'error': 'community_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            return super().list(request, *args, **kwargs)
        except Http404:
            return Response({'error': 'Community not found'}, status=status.HTTP_404_NOT_FOUND)


class UserLastTweetsListView(generics.ListAPIView):
    serializer_class = TweetSerializer
    pagination_class = TwitterUserTweetsPagination
    
    def get_queryset(self):
        user_id = self.request.query_params.get('userId')
        username = self.request.query_params.get('userName')
        include_replies = self.request.query_params.get('includeReplies', 'false').lower() == 'true'
        
        if not user_id and not username:
            return Tweet.objects.none()
        
        if user_id:
            user = get_object_or_404(User, twitter_id=user_id)
        else:
            user = get_object_or_404(User, screen_name=username)
        
        tweets = Tweet.objects.filter(author=user, community__isnull=True)
        if not include_replies:
            tweets = tweets.filter(reply_to__isnull=True)
        
        return tweets
    
    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get('userId')
        username = request.query_params.get('userName')
        
        if not user_id and not username:
            return Response({'error': 'Either userId or userName parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            return super().list(request, *args, **kwargs)
        except Http404:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class TweetRepliesListView(generics.ListAPIView):
    serializer_class = TweetSerializer
    pagination_class = TwitterCursorPagination
    
    def get_queryset(self):
        tweet_id = self.request.query_params.get('tweetId')
        if not tweet_id:
            return Tweet.objects.none()
        
        tweet = get_object_or_404(Tweet, twitter_id=tweet_id)
        return Tweet.objects.filter(reply_to=tweet)
    
    def list(self, request, *args, **kwargs):
        tweet_id = request.query_params.get('tweetId')
        if not tweet_id:
            return Response({'error': 'tweetId parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            return super().list(request, *args, **kwargs)
        except Http404:
            return Response({'error': 'Tweet not found'}, status=status.HTTP_404_NOT_FOUND)


class UserFollowersListView(generics.ListAPIView):
    serializer_class = FollowerSerializer
    pagination_class = TwitterFollowersPagination
    
    def get_queryset(self):
        username = self.request.query_params.get('userName')
        if not username:
            return User.objects.none()
        
        user = get_object_or_404(User, screen_name=username)
        return user.followers.all()
    
    def list(self, request, *args, **kwargs):
        username = request.query_params.get('userName')
        if not username:
            return Response({'error': 'userName parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.paginator.get_paginated_response(serializer.data, 'followers')
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Http404:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UserFollowingsListView(generics.ListAPIView):
    serializer_class = FollowerSerializer
    pagination_class = TwitterFollowersPagination
    
    def get_queryset(self):
        username = self.request.query_params.get('userName')
        if not username:
            return User.objects.none()
        
        user = get_object_or_404(User, screen_name=username)
        return user.following.all()
    
    def list(self, request, *args, **kwargs):
        username = request.query_params.get('userName')
        if not username:
            return Response({'error': 'userName parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.paginator.get_paginated_response(serializer.data, 'followings')
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Http404:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
