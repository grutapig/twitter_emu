import json
from datetime import datetime

import pytz
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from twitterapi.models import Community, Tweet, User


def communities_list(request):
    communities = Community.objects.all().order_by('name')
    data = [{
        'id': community.id,
        'twitter_id': community.twitter_id,
        'name': community.name,
        'tweet_count': community.tweets.count()
    } for community in communities]
    return JsonResponse({'communities': data})


def community_detail(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    page = int(request.GET.get('page', 1))

    tweets = Tweet.objects.filter(community=community).order_by('-created_at')
    paginator = Paginator(tweets, 20)
    page_obj = paginator.get_page(page)

    tweets_data = [{
        'id': tweet.id,
        'twitter_id': tweet.twitter_id,
        'text': tweet.text,
        'author': {
            'id': tweet.author.id,
            'screen_name': tweet.author.screen_name,
            'name': tweet.author.name
        },
        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
        'reply_count': tweet.replies.count()
    } for tweet in page_obj]

    return JsonResponse({
        'community': {
            'id': community.id,
            'twitter_id': community.twitter_id,
            'name': community.name
        },
        'tweets': tweets_data,
        'has_next': page_obj.has_next(),
        'next_page': page + 1 if page_obj.has_next() else None
    })


def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    page = int(request.GET.get('page', 1))

    replies = Tweet.objects.filter(reply_to=tweet).order_by('-created_at')
    paginator = Paginator(replies, 20)
    page_obj = paginator.get_page(page)

    replies_data = [{
        'id': reply.id,
        'twitter_id': reply.twitter_id,
        'text': reply.text,
        'author': {
            'id': reply.author.id,
            'screen_name': reply.author.screen_name,
            'name': reply.author.name
        },
        'created_at': reply.created_at.isoformat() if reply.created_at else None,
        'reply_count': reply.replies.count()
    } for reply in page_obj]

    return JsonResponse({
        'tweet': {
            'id': tweet.id,
            'twitter_id': tweet.twitter_id,
            'text': tweet.text,
            'author': {
                'id': tweet.author.id,
                'screen_name': tweet.author.screen_name,
                'name': tweet.author.name
            },
            'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
            'community': {
                'id': tweet.community.id,
                'name': tweet.community.name
            } if tweet.community else None
        },
        'replies': replies_data,
        'has_next': page_obj.has_next(),
        'next_page': page + 1 if page_obj.has_next() else None
    })


def users_search(request):
    query = request.GET.get('q', '')
    limit = int(request.GET.get('limit', 20))

    users = User.objects.filter(name__icontains=query) if query else User.objects.all()
    users = users.order_by('name')[:limit]

    users_data = [{
        'id': user.id,
        'screen_name': user.screen_name,
        'name': user.name
    } for user in users]

    return JsonResponse({'users': users_data})


def tweet_replies(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    replies = Tweet.objects.filter(reply_to=tweet).order_by('-created_at')

    replies_data = [{
        'id': reply.id,
        'twitter_id': reply.twitter_id,
        'text': reply.text,
        'author': {
            'id': reply.author.id,
            'screen_name': reply.author.screen_name,
            'name': reply.author.name
        },
        'created_at': reply.created_at.isoformat() if reply.created_at else None,
        'reply_count': reply.replies.count()
    } for reply in replies]

    return JsonResponse({'replies': replies_data})


@csrf_exempt
@require_http_methods(["POST"])
def create_tweet(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        author_id = data.get('author_id')
        community_id = data.get('community_id')
        reply_to_id = data.get('reply_to_id')

        if not text or not author_id:
            return JsonResponse({'error': 'Text and author are required'}, status=400)

        author = get_object_or_404(User, id=author_id)
        community = get_object_or_404(Community, id=community_id) if community_id else None
        reply_to = get_object_or_404(Tweet, id=reply_to_id) if reply_to_id else None

        tweet = Tweet.objects.create(
            text=text,
            author=author,
            community=community,
            reply_to=reply_to,
            created_at=datetime.now(pytz.UTC)
        )

        return JsonResponse({
            'tweet': {
                'id': tweet.id,
                'twitter_id': tweet.twitter_id,
                'text': tweet.text,
                'author': {
                    'id': tweet.author.id,
                    'screen_name': tweet.author.screen_name,
                    'name': tweet.author.name
                },
                'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                'reply_count': 0
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    page = int(request.GET.get('page', 1))

    # Filter tweets: only non-reply, non-community tweets (original user posts)
    tweets = Tweet.objects.filter(
        author=user,
        reply_to__isnull=True,  # Not a reply
        community__isnull=True  # Not a community post
    ).order_by('-created_at')

    paginator = Paginator(tweets, 20)
    page_obj = paginator.get_page(page)

    tweets_data = [{
        'id': tweet.id,
        'twitter_id': tweet.twitter_id,
        'text': tweet.text,
        'author': {
            'id': tweet.author.id,
            'screen_name': tweet.author.screen_name,
            'name': tweet.author.name
        },
        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
        'reply_count': tweet.replies.count()
    } for tweet in page_obj]

    # Calculate user stats
    total_tweets = Tweet.objects.filter(author=user).count()
    followers_count = user.followers.count()
    following_count = user.following.count()

    return JsonResponse({
        'user': {
            'id': user.id,
            'twitter_id': user.twitter_id,
            'screen_name': user.screen_name,
            'name': user.name,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None
        },
        'stats': {
            'tweets_count': total_tweets,
            'followers_count': followers_count,
            'following_count': following_count
        },
        'tweets': tweets_data,
        'has_next': page_obj.has_next(),
        'next_page': page + 1 if page_obj.has_next() else None
    })


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    try:
        with transaction.atomic():
            Tweet.objects.filter(reply_to=tweet).delete()
            tweet.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
