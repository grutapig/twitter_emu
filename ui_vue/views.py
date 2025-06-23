from django.shortcuts import render


def home(request):
    return render(request, 'ui_vue/home.html')


def community_detail(request, community_id):
    return render(request, 'ui_vue/community.html', {'community_id': community_id})


def tweet_detail(request, tweet_id):
    return render(request, 'ui_vue/tweet.html', {'tweet_id': tweet_id})


def user_profile(request, user_id):
    return render(request, 'ui_vue/user_profile.html', {'user_id': user_id})