from django.test import TestCase, Client
import json


def data_provider(fn_data_provider):
    """Simple data provider decorator for tests"""
    def test_func_decorator(fn):
        def repl(self, *args):
            for data in fn_data_provider(self):
                fn(self, *data)
        return repl
    return test_func_decorator


class APIEndpointsTest(TestCase):
    fixtures = ['crypto_fixture.json']

    def setUp(self):
        self.client = Client()

    def urls_get_200(self):
        return (
            ('/api/communities/',),
            ('/api/communities/1/',),
            ('/api/communities/2/',),
            ('/api/communities/1/?page=1',),
            ('/api/tweets/1/',),
            ('/api/tweets/39/',),
            ('/api/tweets/59/',),
            ('/api/tweets/1/?page=1',),
            ('/api/tweets/1/replies/',),
            ('/api/tweets/39/replies/',),
            ('/api/tweets/59/replies/',),
            ('/api/users/search/',),
            ('/api/users/search/?q=doge',),
            ('/api/users/search/?q=kitty&limit=5',),
            ('/api/users/1/',),
            ('/api/users/2/',),
            ('/api/users/1/?page=1',),
        )

    @data_provider(urls_get_200)
    def test_get_status200(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, f"GET {url} failed with status {response.status_code}")

    def urls_post_200(self):
        return (
            ('/api/tweets/create/', {
                'text': 'Test tweet from API',
                'author_id': 1
            }, 200),
            ('/api/tweets/create/', {
                'text': 'Test community tweet from API',
                'author_id': 1,
                'community_id': 1
            }, 200),
            ('/api/tweets/create/', {
                'text': 'Test reply from API',
                'author_id': 2,
                'reply_to_id': 1
            }, 200),
        )

    @data_provider(urls_post_200)
    def test_post_status200(self, url, data, expected_status):
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, expected_status, f"POST {url} failed with status {response.status_code}")

    def urls_post_400(self):
        return (
            ('/api/tweets/create/', {
                'text': ''  # Empty text
            }, 400),
            ('/api/tweets/create/', {
                'author_id': 1  # Missing text
            }, 400),
            ('/api/tweets/create/', {
                'text': 'Test'  # Missing author_id
            }, 400),
        )

    @data_provider(urls_post_400)
    def test_post_status400(self, url, data, expected_status):
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, expected_status, f"POST {url} should return {expected_status}")

    def urls_delete_200(self):
        return (
            ('/api/tweets/1/delete/', 200),
            ('/api/tweets/39/delete/', 200),
            ('/api/tweets/59/delete/', 200),
        )

    @data_provider(urls_delete_200)
    def test_delete_status200(self, url, expected_status):
        response = self.client.delete(url)
        self.assertEqual(response.status_code, expected_status, f"DELETE {url} failed with status {response.status_code}")

    def urls_delete_404(self):
        return (
            ('/api/tweets/999/delete/', 404),
            ('/api/tweets/0/delete/', 404),
        )

    @data_provider(urls_delete_404)
    def test_delete_status404(self, url, expected_status):
        response = self.client.delete(url)
        self.assertEqual(response.status_code, expected_status, f"DELETE {url} should return {expected_status}")
