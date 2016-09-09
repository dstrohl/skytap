__all__ = ['BaseDict', 'BaseList']

from collections import UserDict, UserList, namedtuple
from fnmatch import fnmatch

"""
The primary purpose of the BaseDict and BaseList objects is to allow multi-level dictionary access.  so, for example,
you can access a sub dict by passing a key such as 'dict.sub_dict_key', or even a sub-sub dict through a chain of
dict.dict.keys.

This also handles lists as a dictionary item and will pass through a list by including an index in the key-chain.

Finally, you can handle getting lists of keys and sub dict keys out, as well as filtering them and running functions or
converting data on all matching keys in all dicts or lists.
"""


# MLDictKeys = namedtuple('MLDictKeys', 'full_path', 'field_path', 'field')

class MLDictItems(object):
    """
    This is returned by the BaseDict to facilitate handling different types of field names.
    """

    def __init__(self, full_path=True, field_path=True, field=True, parent=None, view_obj_inc='', inc_item=False):
        self._view_obj_inc = view_obj_inc
        self._inc_item = inc_item
        self.full_path = full_path
        self.field_path = field_path
        self.field = field
        self.parent = parent

    def __str__(self):
        return self.full_path

    @property
    def item(self):
        return self.parent[self.field]

    def __bool__(self):
        if self.item:
            return True
        else:
            return False

    @property
    def _get_set(self):
        tmp_ret = []
        if self._view_obj_inc == 'as_full_path' or self._view_obj_inc == '':
            tmp_ret.append(self.full_path)
        if self._view_obj_inc == 'as_field_path' or self._view_obj_inc == '':
            tmp_ret.append(self.field_path)
        if self._view_obj_inc == 'as_field' or self._view_obj_inc == '':
            tmp_ret.append(self.field)
        if self._inc_item:
            tmp_ret.append(self.item)
        return tmp_ret


class BaseCommonFunctions(object):
    _is_dict = False
    _is_list = False
    FIELD = 'as_field'
    FULL_PATH = 'as_full_path'
    FIELD_PATH = 'as_field_path'
    VIEW_OBJ = 'as_view_obj'
    _hash_field = None
    _key_field = None


    def __init__(self, *args, hash_field=None, **kwargs):
        self._hash_field = hash_field
        super(BaseCommonFunctions, self).__init__(*args, **kwargs)

    def _dedupe_list(self, list_in: list, filters=None):
        seen = {}
        result = []

        if filters is not None and not isinstance(filters, (list, tuple)):
            filters = [filters]

        for item in list_in:
            if filters is None or self._filter_item(item, filters):
                if isinstance(item, MLDictItems):
                    key = item.full_path
                else:
                    key = item
                if key in seen:
                    continue
                seen[item] = 1
                result.append(item)
        return result

    @staticmethod
    def _filter_item(item, filters):
        if isinstance(item, MLDictItems):
            for filter in filters:
                if fnmatch(item.full_path, filter):
                    return True
                if fnmatch(item.field_path, filter):
                    return True
            return False

        else:

            for filter in filters:
                if fnmatch(item, filter):
                    return True
            return False

    @staticmethod
    def _make_base(value):
        if isinstance(value, dict):
            return BaseDict(value)
        elif isinstance(value, (list, tuple)):
            return BaseList(value)
        else:
            return value

    def keys(self, recursive=False, scan_all=True, return_as=FIELD, filters=None, **kwargs):
        depth = kwargs.pop('depth', 0)
        path = kwargs.pop('path', '')
        no_list_path = kwargs.pop('no_list_path', '')

        tmp_ret = []
        for rec in enumerate(self.data):
            if self._is_dict:
                key = rec[1]
                item = self.data[key]
            else:
                key = rec[0]
                item = rec[1]

            if path != '':
                tmp_full_path = '%s.%s' % (path, key)
            else:
                tmp_full_path = key

            if no_list_path != '':
                if self._is_dict:
                    tmp_no_list_path = '%s.%s' % (no_list_path, key)
                else:
                    tmp_no_list_path = no_list_path
            else:
                if self._is_dict:
                    tmp_no_list_path = str(key)
                else:
                    tmp_no_list_path = ''

            if isinstance(item, (BaseList, BaseDict)) and recursive:
                tmp_item = item.keys(return_as=return_as, recursive=recursive,
                                     scan_all=scan_all, path=tmp_full_path, no_list_path=tmp_no_list_path,
                                     depth=depth + 1, filters=filters, **kwargs)
                tmp_ret.extend(tmp_item)

            else:
                if return_as == self.VIEW_OBJ:
                    tmp_obj = MLDictItems(
                        full_path=tmp_full_path,
                        field_path=tmp_no_list_path,
                        field=key,
                        parent=self,
                        **kwargs
                    )
                    tmp_ret.append(tmp_obj)
                elif return_as == self.FIELD_PATH:
                    tmp_ret.append(tmp_no_list_path)
                elif return_as == self.FULL_PATH:
                    tmp_ret.append(tmp_full_path)
                else:
                    tmp_ret.append(key)

            if self._is_list and not scan_all and not return_as == self.FULL_PATH:
                break

        if depth == 0:
            tmp_ret = self._dedupe_list(tmp_ret, filters=filters)
        return tmp_ret

    def items(self, recursive=False, return_as=FULL_PATH, filters=None):

        tmp_ret = self.keys(recursive=recursive, scan_all=True,
                            return_as=self.VIEW_OBJ, view_obj_inc=return_as, filters=filters, inc_item=True)

        if return_as == self.VIEW_OBJ:
            return tmp_ret
        else:
            tmp_ret_list = []
            for item in tmp_ret:
                tmp_ret_list.append(item._get_set)
            return tmp_ret_list

    def convert(self, func, *fields, **kwargs):
        tmp_list = self.items(recursive=True, return_as=self.VIEW_OBJ, filters=fields)
        count = 0
        for item in tmp_list:
            count += 1
            self[item.full_path] = func(item.item, **kwargs)
        return count

    def run(self, func, *fields, **kwargs):
        tmp_list = self.items(recursive=True, return_as=self.VIEW_OBJ, filters=fields)
        tmp_ret = []
        for item in tmp_list:
            tmp_ret.append(func(item.item, **kwargs))
        return tmp_ret

    @property
    def _name_(self):
        if self._is_dict:
            return 'BaseDict'
        else:
            return 'BaseList'

    @property
    def _hash_field_(self):
        if self._hash_field is None:
            return self._key_field
        else:
            return self._hash_field

    def _item_contains(self, key, item):
        if isinstance(item, BaseDict):
            return key in item
        elif isinstance(item, BaseList):
            return item.contains_field(key)
        else:
            return False


class BaseDict(BaseCommonFunctions, UserDict):
    def __init__(self, *args, **kwargs):
        # self._path = path
        # self._no_list_path=no_list_path
        self._is_dict = True
        # self._dict_items = []
        # self._list_items = []

        super(BaseDict, self).__init__(*args, **kwargs)

    def __getitem__(self, item):

        if '.' in item:
            my_item, sub_item = item.split('.', 1)
            if my_item not in self.data:
                raise KeyError('"%s" is not in this dict.  available fields include: %s' % (my_item, self.keys()))
            return self.data[my_item][sub_item]
        return self.data[item]

    def __getattr__(self, item):
        return self[item]

    def __setitem__(self, item, value):

        if '.' in item:

            my_item, sub_item = item.split('.', 1)
            if my_item not in self.data:
                raise KeyError(
                    '"%s" is not in this dict to set.  available fields include: %s' % (my_item, self.keys()))

            self.data[my_item][sub_item] = self._make_base(value)
        else:
            self.data[item] = self._make_base(value)

    def __delitem__(self, item):
        if '.' in item:
            my_item, sub_item = item.split('.', 1)
            if my_item not in self.data:
                raise KeyError('"%s" is not in this dict.  available fields include: %s' % (my_item, self.keys()))
            del self.data[my_item][sub_item]
        else:
            del self.data[item]


    def __contains__(self, item):
        if item in self.data:
            return True
        try:
            tmp_trash = self[item]
            return True
        except (KeyError, AttributeError):
            if '.' in item:
                my_item, sub_item = item.split('.', 1)
                if my_item not in self.data:
                    return False
                tmp_my_item = self.data[my_item]
                return self._item_contains(sub_item, tmp_my_item)
        except TypeError:
            return False

    def __hash__(self):

        if self._hash_field_ is None:
            raise TypeError(
                '%s cannot be hashed without setting a hash field or key field' % self._name_)
        try:
            return hash(self[self._hash_field_])
        except KeyError:
            raise TypeError(
                'the defined hash field %s[%s] is not present' % (self._name_, self._hash_field_))


class BaseList(BaseCommonFunctions, UserList):
    def __init__(self, *args, **kwargs):
        # self._no_list_path = no_list_path
        # self._path = path
        super(BaseList, self).__init__(*args, **kwargs)
        for index, item in enumerate(self.data):
            self.data[index] = self._make_base(item)
        self._is_list = True

    def insert(self, index, value):
        self.data.insert(index, self._make_base(value))

    def extend(self, other):
        for item in other:
            self.append(item)

    def append(self, value):
        index = len(self.data)

        self.data.append(self._make_base(value))

    def __getitem__(self, item):
        if isinstance(item, str) and '.' in item:
            my_index, sub_item = item.split('.', 1)
            is_slice, index = self._make_index(my_index)
            if is_slice:
                return BaseList(self.data[index][sub_item])
            else:
                return self.data[index][sub_item]
        is_slice, item = self._make_index(item)
        if is_slice:
            return BaseList(self.data[item])
        else:
            return self.data[item]

    def __delitem__(self, item):
        if isinstance(item, str) and '.' in item:
            my_index, sub_item = item.split('.', 1)
            is_slice, index = self._make_index(my_index)
            del self.data[index][sub_item]
        else:
            is_slice, index = self._make_index(item)
            del self.data[index]

    def _make_index(self, index):
        # returns (<True|False is Slice>, <new index value>)
        if isinstance(index, int):
            return False, index
        if isinstance(index, slice):
            return True, index
        if isinstance(index, str) and ':' in index:
            tmp_args = index.split(':')
            for slice_index, arg in enumerate(tmp_args):
                try:
                    tmp_args[slice_index] = int(arg)
                except ValueError:
                    raise AttributeError('slice passed ("%s") cannot be converted to a slice' % index)
            tmp_slice = slice(*tmp_args)
            return True, tmp_slice
        else:
            try:
                return False, int(index)
            except ValueError:
                raise AttributeError('index passed ("%s") cannot be converted to an int' % index)

    def __setitem__(self, item, value):
        if isinstance(item, str):
            if '.' in item:

                my_item, sub_item = item.split('.', 1)
                try:
                    my_item = int(my_item)
                except ValueError:
                    raise AttributeError('index passed ("%s") cannot be converted to an int' % my_item)
                self.data[my_item][sub_item] = self._make_base(value)
            else:
                try:
                    self.data[int(item)] = self._make_base(value)
                except ValueError:
                    raise AttributeError('index passed ("%s") cannot be converted to an int' % item)
        else:
            self.data[item] = self._make_base(value)


    def contains_field(self, item):
        if isinstance(item, str):
            if '.' in item:
                my_item, sub_item = item.split('.', 1)
                if my_item.isnumeric():
                    tmp_item = self.data[int(my_item)]
                    return self._item_contains(sub_item, tmp_item)
                item = my_item

            for my_item in self.data:
                if item in my_item:
                    return True
            return False
        else:
            return item < len(self.data)

    def __contains__(self, item):
        if item in self.data:
            return True
        else:
            return self.contains_field(item)

    def __hash__(self):
        if self._hash_field_ is None:
            raise TypeError(
                'unhashable type: %s cannot be hashed without setting a hash field or key field' % self._name_)

        tmp_list = []
        for item in self.data:
            try:
                tmp_list.append(str(hash(item[self._hash_field])))
            except KeyError:
                raise TypeError('unhashable type: %s cannot be hashed, %s not in %s' %
                                (self._name_, self._hash_field, item))
            except TypeError:
                raise TypeError('unhashable type: %s cannot be hashed, value in field %s is not hashable' %
                                (self._name_, self._hash_field))
        return hash('.'.join(tmp_list))

