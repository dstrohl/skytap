"""Support for a single sharing portal (was called published set) in a Skytap environment or vm."""
from skytap.models.SkytapResource import SkytapResource
from skytap.models.NewBase import NewSTResource
"""
Field Def schema
field_defs = dict(
    <field_name>=dict(
        type='<*str|date|datetime|time|timezone|int|bool|double|array>',
        required=True|*False,
        sub_rec_def=<schema dict | *None>,

* = defaults
"""
SHARING_PORTAL_WRITABLE_FIELDS = [
    'name', 'publish_set_type', 'runtime_limit', 'expiration_date', 'expiration_date_tz', 'start_time', 'end_time',
    'time_zone', 'password', 'sso_required', 'vms', 'vms.vm_ref', 'vms.access', 'anonymous_smart_rdp',
    'custom_content_enabled', 'custom_title', 'custom_content', 'custom_content_is_default']

SHARING_PORTAL_FIELD_DEFS = {
    'id': {'type': 'int'},
    'name': {'required': True},
    'runtime_limit': {'type': 'int'},
    'runtime_left_in_seconds': {'type': 'int'},
    'expiration_date': {'type': 'datetime', 'tz': 'expiration_date_tz'},
    'expiration_date_tz': {'type': 'timezone'},
    'start_time': {'type': 'time', 'tz': 'time_zone'},
    'end_time': {'type': 'time', 'tz': 'time_zone'},
    'time_zone': {'type': 'timezone'},
    'multiple_url': {'type': 'bool'},
    'sso_required': {'type': 'bool'},
    'vms.id': {'type': 'int'},
    'vms.use_and_run': {'type': 'bool'},
    'vms.error': {'type': 'bool'},
    'anonymous_smart_rdp': {'type': 'bool'},
    'custom_content_enabled': {'type': 'bool'},
    'custom_content_is_default': {'type': 'bool'},
}

class SharingPortal(NewSTResource, SkytapResource):

    """One note."""
    _writable_fields = SHARING_PORTAL_WRITABLE_FIELDS
    _field_defs = SHARING_PORTAL_FIELD_DEFS

    def __init__(self, portal_json):
        super(SharingPortal, self).__init__(portal_json)


        self._new_convert_data_elements()

