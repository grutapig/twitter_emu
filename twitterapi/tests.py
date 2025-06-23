from rest_framework.test import APITestCase


def data_provider(fn_data_provider):
    """Simple data provider decorator for tests"""

    def test_func_decorator(fn):
        def repl(self, *args):
            for data in fn_data_provider(self):
                fn(self, *data)

        return repl

    return test_func_decorator


class TwitterAPIEndpointsTest(APITestCase):
    fixtures = ['crypto_fixture.json']

    def urls_get_200(self):
        return (
            ('/twitter/community/tweets/?community_id=9876543210987654321',),
            ('/twitter/user/last_tweets/?userName=kitty_creator',),
            ('/twitter/user/last_tweets/?userId=1111111111111111111&include_replies=true',),
            ('/twitter/user/last_tweets/?userId=1111111111111111111&include_replies=false',),
            ('/twitter/tweet/replies/?tweetId=1001001001001001056',),
            ('/twitter/tweet/replies/?tweetId=1001001001001001055',),
            ('/twitter/user/followers/?userName=kitty_creator',),
            ('/twitter/user/followers/?userName=doge_founder',),
            ('/twitter/user/followings/?userName=doge_founder',),
        )

    @data_provider(urls_get_200)
    def test_get_status200(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, f"GET {url} failed with status {response.status_code}")
