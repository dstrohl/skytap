"""Base class for all Skytap Resources."""
import json

from skytap.framework.ApiClient import ApiClient  # noqa
from skytap.framework.Json import SkytapJsonEncoder  # noqa
import skytap.framework.Utils as Utils  # noqa

bool_fix = {'true': True, 'True': True, 'TRUE': True, 'Yes': True, True: True,
            'false': False, 'False': False, 'FALSE': False, 'No': False, False: False}


class SkytapResource(object):

    """Represents one Skytap Resource - a VM, Environment, User, whatever."""
    _default_field_defs = dict(
        created_at = {'type': 'datetime'},
        last_login={'type': 'datetime'},
        last_run={'type': 'datetime'},
        updated_at={'type': 'datetime'},
        last_installed={'type': 'datetime'},
        id={'type': 'int'},
    )
    _writable_fields = None
    _field_defs = None
    _required_fields = None
    _sub_models = {}
    # usage:
    #       _sub_models = {'vms': {'aliases':('virtual_machines','virtual_systems'),'model':Vms, 'url_ext':'/vms'}
    #       _sub_models = {'vms': Vms}
    #       if aliases are defined, any of these can be used to call the data, but it is stored under the main
    #       dictionary key.  (these can be used when things are renamed)
    #       if the url_ext is not defined, we will look for the _ext_url property of the model, then try name of the model.
    _field_aliases = {}

    def __init__(self, initial_json):
        super(SkytapResource, self).__init__()

        self.data = {}
        self.data["id"] = 0
        for k in initial_json.keys():
            self.data[k] = initial_json[k]
        if 'url' in self.data:
            if '/v2/' in self.url:
                self.data['url_v1'] = self.url.replace('/v2/', '/')
                self.data['url_v2'] = self.url
            else:
                self.data['url_v1'] = self.url
                self.data['url_v2'] = None

        if self._field_defs is not None:
            self._default_field_defs.update(self._field_defs)
        if self._required_fields is None:
            self._required_fields = []

        # clean up field definitions (adding default fields, validating fields, etc)
        for field_name, field_def in self._default_field_defs.items():
            if 'required' in field_def:
                self._required_fields.append(field_name)
            if field_def.get('type', 'str') == 'tz':
                if field_def['tz'] not in self._default_field_defs:
                    raise KeyError('Field definitions error: TZ field %s missing (used by field %s)' %
                                   (field_def['tz'], field_name))
                if 'used_by' not in self._default_field_defs[field_def['tz']]:
                    self._default_field_defs[field_def['tz']]['used_by'] = [field_name]
                else:
                    self._default_field_defs[field_def['tz']]['used_by'].append([field_name])

        # cleaning up sub_model list
        for sub_model in self._sub_models.keys():
            defs = self._sub_models[sub_model]
            if isinstance(defs, dict):
                if 'aliases' in defs:
                    for alias in defs['aliases']:
                        self._field_aliases[alias] = sub_model
            else:
                self._sub_models[sub_model] = {'model': defs}

            if 'url_ext' not in self._sub_models[sub_model]:
                try:
                    self._sub_models[sub_model]['ext_url'] = self._sub_models[sub_model]['model']._url_ext
                except AttributeError:
                    tmp_url_ext = self._sub_models[sub_model]['model'].__class__.__name__
                    self._sub_models[sub_model]['ext_url'] = '/%s.json' % tmp_url_ext.lower()

        self._convert_data_elements()
        self._calculate_custom_data()

    def _calculate_custom_data(self):
        """Used so objects can create and calculate new data elements."""
        pass

    def _convert_data_elements(self):
        """Convert some data elements into variable types that make sense."""

        if hasattr(self, '_field_defs'):
            for field_name, field_def in self._default_field_defs.items():
                if '.' in field_name:
                    fn1, fn2 = field_name.split('.', 1)
                    try:
                        for sub_field_index in range(len(self.data[fn1])):
                            tmp_value = self.data[fn1][sub_field_index][fn2]
                            if tmp_value is not None:
                                tmp_value = self._convert_data_item(field_def, tmp_value)
                                self.data[fn1][sub_field_index][fn2] = tmp_value
                    except (KeyError, ValueError, AttributeError):
                        pass
                else:
                    try:
                        tmp_value = self.data[field_name]
                        if tmp_value is not None:
                            tmp_value = self._convert_data_item(field_def, tmp_value)
                            self.data[field_name] = tmp_value
                    except (KeyError, ValueError, AttributeError):
                        pass

    def _convert_data_item(self, field_def, current_value):
        if 'type' in field_def:
            data_type = field_def['type']
            try:
                if data_type == 'str':
                    return str(current_value)
                elif data_type == 'int':
                    return int(current_value)
                elif data_type == 'bool':
                    return bool_fix[current_value]
                elif data_type in ('date', 'datetime', 'time'):
                    if 'tz' in field_def:
                        return Utils.convert_date(current_value, self._default_field_defs[field_def['tz']])
                elif data_type == 'timezone':
                    return current_value
                elif data_type == 'float':
                    return float(current_value)
            except:
                return current_value
        else:
            return current_value

    def refresh(self):
        """Refresh the data in our object, if we have a URL to pull from."""
        if 'url' not in self.data:
            return KeyError
        api = ApiClient()
        env_json = api.rest(self.url)
        self.__init__(json.loads(env_json))

    def __getattr__(self, key):
        key = self._field_defs.get(key, key)

        if key in self._sub_models:
            api = ApiClient()
            tmp_json = api.rest(self.url + self._sub_models[key]['ext_url'])
            tmp_obj = self._sub_models[key]['model']
            tmp_ret = tmp_obj(tmp_json, self.url)
            return tmp_ret

        if key not in self.data:
            raise AttributeError

        return self.data[key]


    def json(self, only_writable=False, error_on_required=False, skip_none=False, indent=4):
        """Convert the object to JSON."""
        tmp_data = self._pre_json_conversion(only_writable, error_on_required, skip_none)
        return json.dumps(tmp_data, indent=indent, cls=SkytapJsonEncoder)

    def _pre_json_conversion(self, only_writable=False, error_on_required=False, skip_none=False):
        """
        Convert objects to json that the standard conversion wont work with.
        this is separate from the existing skytap.utils.json modification to allow things like
        date/time conversion based on the specific type of object.
        """
        if self._writable_fields is None:
            self._writable_fields = {}
        tmp_del_fields = []
        tmp_ret_dict = self.data.copy()

        # check for required fields
        if error_on_required:
            for key in self._required_fields:
                if '.' in key:
                    fn1, fn2 = key.split('.', 1)
                    for sub_field_index in range(len(self.data[fn1])):
                        if fn2 not in self.data[fn1][sub_field_index]:
                            raise AttributeError('Missing required field: %s[%s].%s' % (fn1, sub_field_index, fn2))
                else:
                    if key not in self.data:
                        raise AttributeError('Missing required field: %s' % key)
        # convert fields that json wont be able to
        for field_name, field_def in self._default_field_defs.items():
            if not only_writable or field_name in self._writable_fields:
                if '.' in field_name:
                    fn1, fn2 = field_name.split('.', 1)
                    try:
                        for sub_field_index in range(len(tmp_ret_dict[fn1])):
                            tmp_value = self._get_for_json(
                                field_name=fn2,
                                get_from=tmp_ret_dict[fn1][sub_field_index],
                                get_sub_models=False,
                                recurse=False)
                            tmp_ret_dict[fn1][sub_field_index][fn2] = tmp_value
                    except (KeyError, ValueError, AttributeError):
                        pass
                else:
                    try:
                        tmp_ret_dict[field_name] = self._get_for_json(
                            field_name=field_name,
                            get_from=tmp_ret_dict,
                            get_sub_models=False,
                            recurse=False)
                    except (KeyError, ValueError, AttributeError):
                        pass

        # check for writable and none:
        tmp_fields = list(tmp_ret_dict)
        for key in tmp_fields:
            if self._block_field(tmp_ret_dict[key], key, only_writable, skip_none):
                del tmp_ret_dict[key]
            else:
                if isinstance(tmp_ret_dict[key], (list, tuple)):
                    for index, item in enumerate(tmp_ret_dict[key]):
                        if self._block_field(tmp_ret_dict[key][index][item], key, only_writable, skip_none, item):
                            del tmp_ret_dict[key][index][item]

                elif isinstance(tmp_ret_dict[key], dict):
                    for item in list(tmp_ret_dict[key]):
                        if self._block_field(tmp_ret_dict[key][item], key, only_writable, skip_none, item):
                            del tmp_ret_dict[key][item]
        return tmp_ret_dict

    def _block_field(self, value, fieldname, only_writable, skip_none, sub_fieldname=None):
        if sub_fieldname is not None:
            fieldname = '%s.%s' % (fieldname, sub_fieldname)
        if only_writable and fieldname not in self._writable_fields:
            return True
        elif skip_none and value is None:
            return True
        return False

    def _get_for_json(self, field_name, get_from=None, get_sub_models=False, recurse=False):
        """
        called by the pre_json_conversion for each field needing conversion.

            (pulling data direct from the source dict rather than converting it to handle the sub-models,
            or, not handle them, as the case may be.).

        :param field_name: the field name to return
        :type field_name: str
        :param get_sub_models: if sub models are defined, should we get them from Skytap for this
        :type get_sub_models: bool
        :param recurse: should we recurse through all sub models
        :type recurse: bool
        """
        if get_from is None:
            get_from = self.data

        if field_name in self._sub_models:
            if get_sub_models:
                tmp_obj = getattr(self, field_name)
                if recurse:
                    return tmp_obj.json(get_sub_models=True, recurse=True)
                else:
                    return tmp_obj.json()
            else:
                raise KeyError('Model for field %s not downloaded' % field_name)

        if field_name not in get_from:
            raise KeyError('Field %s does not exist in this dataset' % field_name)

        # ****************** start conversions **********************************

        if get_from[field_name] is None:
            return None

        if field_name in self._default_field_defs:
            field_def = self._default_field_defs[field_name]
            if field_def['type'] in ('date', 'datetime', 'time'):
                tmp_dt = get_from[field_name]
                tmp_tz = get_from.get(field_def['tz'], 'default')
                tmp_ret_tz = 'tz' in field_def
                tmp_ret_as = field_def['type']
                return Utils.convert_date_for_json(
                    tmp_dt,
                    return_as=tmp_ret_as,
                    ret_tz=tmp_ret_tz,
                    ret_as_tz=tmp_tz)

        else:
            return get_from[field_name]

        # ****************** start conversions **********************************

    def __str__(self):
        return str(self.name)

    def __int__(self):
        return int(self.id)

    def __gt__(self, other):
        return int(self) > int(other)

    def __lt__(self, other):
        return int(self) < int(other)

    def __hash__(self):
        return hash(repr(self.data))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __contains__(self, key):
        return key in self.data
