import json
import os
import sys

sys.path.append('..')
from skytap.models.Environment import Environment  # noqa
from skytap.models.SkytapGroup import SkytapGroup  # noqa
from skytap.framework.Fixtures import ResponseConfig
from skytap.framework.Config import Config

Config.api_is_test_fixture = True

configurations_req = ResponseConfig(
    match_url='*/v2/configurations',
    text=[
        {'id': 1, 'name': 'test_1', 'runstate': 'running', 'vms': [], 'url': '/v2/configurations/1'},
        {'id': 2, 'name': 'test_2', 'runstate': 'running', 'vms': [], 'url': '/v2/configurations/2'}
    ],
    priority=10,
)

configurations_req_param = ResponseConfig(
    match_url='*/v2/configurations',
    match_params={'scope': 'company'},
    text=[
        {'id': 3, 'name': 'test_3', 'runstate': 'running', 'vms': [], 'url': '/v2/configurations/3'},
        {'id': 4, 'name': 'test_4', 'runstate': 'running', 'vms': [], 'url': '/v2/configurations/4'},
        {'id': 5, 'name': 'test_5', 'runstate': 'running', 'vms': [], 'url': '/v2/configurations/5'},
        {'id': 6, 'name': 'test_6', 'runstate': 'running', 'vms': [], 'url': '/v2/configurations/6'},
    ],
    priority=5,
)


class SkytapGroupToTest(SkytapGroup):

    _is_test_fixture = True

    def __init__(self):
        super(SkytapGroupToTest, self).__init__()

group = SkytapGroupToTest()

group._sim_manager.add_response_config(
    configurations_req,
    configurations_req_param)

class TestSkytapGroup(object):
    def test_load_from_api(self):
        group.load_list_from_api('/v2/configurations', Environment)
        assert len(group) == 2

    def test_load_from_api_with_parameter(self):
        group.load_list_from_api('/v2/configurations',
                                 Environment, {'scope': 'company'})
        assert len(group) == 4
