import sys
import json
from unittest import TestCase

from skytap.framework.Fixtures import ResponseConfig
from skytap.framework.ApiClient import ApiClient
from skytap.framework.ApiExceptions import *

sys.path.append('..')

test_1_text = """
{
    "employees": {
        "employee": [
            {
                "id": "1",
                "firstName": "Tom",
                "lastName": "Cruise",
                "photo": "http://cdn2.gossipcenter.com/sites/default/files/imagecache/story_header/photos/tom-cruise-020514sp.jpg"
            },
            {
                "id": "2",
                "firstName": "Maria",
                "lastName": "Sharapova",
                "photo": "http://thewallmachine.com/files/1363603040.jpg"
            },
            {
                "id": "3",
                "firstName": "James",
                "lastName": "Bond",
                "photo": "http://georgesjournal.files.wordpress.com/2012/02/007_at_50_ge_pierece_brosnan.jpg"
            }
        ]
    }
}
"""
test_1_json = json.loads(test_1_text)

rc_200_std = ResponseConfig(
    match_url='https://cloud.skytap.com/',
    text='{"name": "test_2"}',
    status_code=200,
    priority=100,
)

rc_300_std = ResponseConfig(
    match_url='https://cloud.skytap.com/Error',
    text='Error 300',
    status_code=300,
    priority=100,
)
rc_200_pre_star = ResponseConfig(
    match_url='*/pre_star',
    text='{"name": "rc_200_pre_star"}',
    status_code=200,
    priority=100,
)
rc_200_post_star = ResponseConfig(
    match_url='https://cloud.skytap.com/post_star/*',
    text='{"name": "rc_200_post_star"}',
    status_code=200,
    priority=100,
)
rc_404_any_star = ResponseConfig(
    match_url='*',
    text='page not found',
    status_code=404,
    priority=999,
)
rc_200_text_resp = ResponseConfig(
    match_url='*/text/',
    text='text_resp',
    status_code=200,
    priority=100,
)

all_responses = [
    rc_200_std,
    rc_300_std,
    rc_200_pre_star,
    rc_200_post_star,
    rc_200_text_resp,
    rc_404_any_star,
]

class TestApiClient(ApiClient):
    _is_test_fixture = True


class TestResponseFixture(TestCase):
    maxDiff = None

    def setUp(self):
        self.api = TestApiClient()
        self.api._sim_manager.add_response_config(*all_responses)


    def test_basic_response(self):
        api = TestApiClient()
        api._sim_manager.add_response_config({
            'match_url': 'https://cloud.skytap.com/',
            'text': test_1_text,
            'resp_code': 200,
        })
        test_resp = api.rest('/')
        test_resp_json = json.loads(test_resp)
        # print(test_resp)
        self.assertEqual(test_resp_json, test_1_json)


    def test_star_response(self):

        with self.subTest('rc_200_std'):
            test_resp = self.api.rest('/')
            self.assertEqual(test_resp, rc_200_std)

        with self.subTest('rc_300_std'):
            with self.assertRaises(SkytapOtherSystemError):
                test_resp = self.api.rest('/Error')
                self.assertEqual(test_resp, rc_300_std)

        with self.subTest('rc_200_pre_star'):
            test_resp = self.api.rest('/hello/pre_star')
            self.assertEqual(test_resp, rc_200_pre_star)

        with self.subTest('rc_200_post_star'):
            test_resp = self.api.rest('/post_star/blah.html')
            self.assertEqual(test_resp, rc_200_post_star)

        with self.subTest('rc_404_any_star'):
            with self.assertRaises(Skytap404NotFoundError):
                test_resp = self.api.rest('/foobar')

        with self.subTest('rc_200_text_resp'):
            test_resp = self.api.rest('/text/')
            self.assertEqual(test_resp, rc_200_text_resp)

