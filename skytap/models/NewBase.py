from skytap.framework.Utils import convert_date


bool_fix = {'true': True, 'True': True, 'TRUE': True, 'Yes': True, True: True,
            'false': False, 'False': False, 'FALSE': False, 'No': False, False: False}


class NewSTResource(object):

    _writable_fields = None
    _field_defs = None

    # def __init__(self, *args, **kwargs):

    def _new_convert_data_elements(self):
        if hasattr(self, '_field_defs'):
            for field_name, field_def in self._field_defs.items():
                if '.' in field_name:
                    fn1, fn2 = field_name.split('.', 1)
                    if fn1 in self and isinstance(self.data[fn1], (list, tuple)):
                        for sub_field_index in range(len(self.data[fn1])):
                            if fn2 in self.data[fn1][sub_field_index]:
                                tmp_value = self.data[fn1][sub_field_index][fn2]
                                tmp_value = self._convert_data_item(field_def, tmp_value)
                                self.data[fn1][sub_field_index][fn2]
                else:
                    if field_name in self:
                        tmp_value = self.data[field_name]
                        tmp_value = self._convert_data_item(field_def, tmp_value)
                        self.data[field_name] = tmp_value

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
                        return convert_date(current_value, self._field_defs[field_def['tz']])
                elif data_type == 'timezone':
                    return current_value
                elif data_type == 'float':
                    return float(current_value)
            except:
                return current_value
        else:
            return current_value








