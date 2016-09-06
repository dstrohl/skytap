"""Test Skytap SharingPortal API access."""
import json
import os
import sys
from datetime import date, datetime, time

sys.path.append('..')
from skytap.Environments import Environments  # noqa
from skytap.models.SharingPortals import SharingPortals
from skytap.framework.Config import Config
try:
    from skytap_token import SKYTAP_TOKEN, SKYTAP_USER
except:
    raise EnvironmentError('No skytap token file')


Config(SKYTAP_USER, SKYTAP_TOKEN)

SKYTAP_ENV_WITH_SHARING_PORTAL = 9665596

environment = Environments()[SKYTAP_ENV_WITH_SHARING_PORTAL]
portals = environment.sharing_portals
portal = portals.first()

def test_get_sharing_portal():
    assert len(portals) >= 1

def test_sp_field_defs():
    assert isinstance(portal.id, int)
    assert isinstance(portal.runtime_limit, int) or portal.runtime_limit is None
    assert isinstance(portal.expiration_date, datetime) or portal.expiration_date is None
    assert isinstance(portal.runtime_left_in_seconds, int) or portal.runtime_left_in_seconds is None

    assert isinstance(portal.multiple_url, bool)
    assert isinstance(portal.sso_required, bool)
    assert isinstance(portal.anonymous_smart_rdp, bool)
    assert isinstance(portal.custom_content_enabled, bool)
    assert isinstance(portal.custom_content_is_default, bool)

    assert isinstance(portal.end_time, time) or portal.end_time is None

    assert isinstance(portal.start_time, time) or portal.start_time is None

    for vm in portal.vms:
        assert isinstance(vm['id'], int)
        assert isinstance(vm['run_and_use'], bool)
        assert isinstance(vm['error'], bool)


def test_environment_id():
    """Ensure environments have ids."""
    for l in list(portals.data):
        e = portals[l]
        assert e.id > 0


def test_environment_json():
    """Ensure environment json conversion seems to be working."""
    for l in list(portals.data):
        e = portals[l]
        assert len(json.dumps(e.json())) > 0


def test_environment_str_conversion():
    """Ensure environment str converion works."""
    for l in list(portals.data):
        e = portals[l]
        assert str(e) == e.name
