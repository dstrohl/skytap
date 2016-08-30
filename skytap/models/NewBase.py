from skytap.framework.Utils import convert_date


bool_fix = {'true': True, 'True': True, 'TRUE': True, 'Yes': True, True: True,
            'false': False, 'False': False, 'FALSE': False, 'No': False, False: False}


class NewSTResource(object):

    _writable_fields = None
    _field_defs = None

    def __init__(self, **args, **kwargs):
        self._new_convert_data_elements()

    def _new_convert_data_elements(self):
        if hasattr(self, '_field_defs'):
            for field_name, field_def in self._field_defs.items():
                if '.' in field_name:
                    fn1, fn2 = field_name.split('.',1)
                    tmp_value = getattr(getattr(self, fn1), fn2)
                    tmp_value = self._convert_data_item(field_def, tmp_value)
                    setattr(getattr(self, fn1), fn2, tmp_value)
                else:
                    tmp_value = getattr(self, field_name)
                    tmp_value = self._convert_data_item(field_def, tmp_value)
                    setattr(self, field_name, tmp_value)

    def _convert_data_item(self, field_def, current_value):
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
                    return convert_date(current_value, self._field_defs[field_def['tz']])
            elif data_type == 'timezone':
                return current_value
            elif data_type == 'float':
                return float(current_value)
        except:
            return current_value









