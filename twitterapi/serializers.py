from rest_framework import serializers

from .models import User, Tweet, Community


class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='twitter_id')
    userName = serializers.CharField(source='screen_name')
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at', format='%a %b %d %H:%M:%S +0000 %Y')

    class Meta:
        model = User
        fields = ['id', 'userName', 'name', 'followers', 'following', 'createdAt']

    def get_followers(self, obj):
        return obj.followers.count()

    def get_following(self, obj):
        return obj.following.count()


class CommunitySerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='twitter_id')
    createdAt = serializers.DateTimeField(source='created_at', format='%a %b %d %H:%M:%S +0000 %Y')

    class Meta:
        model = Community
        fields = ['id', 'name', 'createdAt']


class TweetSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='twitter_id')
    author = AuthorSerializer(read_only=True)
    community = CommunitySerializer(read_only=True, allow_null=True)
    replyCount = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at', format='%a %b %d %H:%M:%S +0000 %Y')
    inReplyToId = serializers.CharField(source='reply_to.twitter_id', allow_null=True)
    conversationId = serializers.SerializerMethodField()
    isReply = serializers.SerializerMethodField()
    isCommunityPost = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = ['id', 'text', 'author', 'community', 'replyCount', 'createdAt', 'inReplyToId', 'conversationId', 'isReply', 'isCommunityPost']

    def get_replyCount(self, obj):
        return obj.replies.count()

    def get_conversationId(self, obj):
        return obj.reply_to.twitter_id if obj.reply_to else obj.twitter_id

    def get_isReply(self, obj):
        return obj.reply_to is not None

    def get_isCommunityPost(self, obj):
        return obj.community is not None


class FollowerSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='twitter_id')
    screen_name = serializers.CharField()
    userName = serializers.CharField(source='screen_name')
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%a %b %d %H:%M:%S +0000 %Y')

    class Meta:
        model = User
        fields = ['id', 'name', 'screen_name', 'userName', 'followers_count', 'following_count', 'created_at']

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()
