from unittest import TestCase
from skytap.framework.BaseDictList import BaseDict, BaseList


def conversion_fixture(data_in, conversion_type=None):
    if conversion_type is None:
        return data_in+'-C'
    if conversion_type == 'int':
        return int(data_in)


def run_fixture(data_in, in_dict=False):
    if in_dict:
        return {'value': data_in}
    else:
        return data_in


class TestBaseDict(TestCase):

    def test_dict(self):
        test_name = 'base test'
        test_dict = {'f1': 'F1', 'f2': 'F2'}
        bd = BaseDict(test_dict)

        with self.subTest('%s get_item' % test_name):
            self.assertEqual(bd['f1'], 'F1')

        with self.subTest('%s set_exist_item' % test_name):
            bd['f2'] = 'blah'
            self.assertEqual(bd['f2'], 'blah')

        with self.subTest('%s set_new_item' % test_name):
            bd['f3'] = 'F3'
            self.assertEqual(bd['f3'], 'F3')

        with self.subTest('%s get_attr' % test_name):
            self.assertEqual(bd.f2, 'blah')

        with self.subTest('%s del' % test_name):
            del bd['f2']
            self.assertEqual(len(bd), 2)

        with self.subTest('%s get' % test_name):
            self.assertEqual(bd.get('f1'), 'F1')

        with self.subTest('%s get_empty' % test_name):
            self.assertEqual(bd.get('bar'), None)

        with self.subTest('%s update' % test_name):
            test_dict2 = {'f4': 'F4', 'f5': 'F5'}
            bd.update(test_dict2)
            self.assertEqual(bd['f4'], 'F4')

        with self.subTest('%s update_overlap' % test_name):
            test_dict2 = {'f1': 'B1', 'f6': 'F6'}
            bd.update(test_dict2)
            self.assertEqual(bd['f1'], 'B1')

        with self.subTest('%s update_check_type' % test_name):
            test_dict2 = {'f7': {'B1': 'B1', 'b2': 'B2'}, 'f8': ['1,2,3']}
            bd.update(test_dict2)
            self.assertTrue(isinstance(bd['f7'], BaseDict))
            self.assertTrue(isinstance(bd['f8'], BaseList))

        with self.subTest('%s additem_check_type' % test_name):
            bd['add_dict'] = {'B1': 'B1', 'b2': 'B2'}
            self.assertTrue(isinstance(bd['add_dict'], BaseDict))
            bd['add_list'] = ['1',2,3]
            self.assertTrue(isinstance(bd['add_list'], BaseList))



    def test_2_level_dict(self):
        test_name = 'base test'
        test_dict = {'f1': 'F1', 'f2': 'F2', 'f3': {'f1': 'F3.1', 'f2': 'F3.2'}}
        bd = BaseDict(test_dict)

        with self.subTest('%s get_item' % test_name):
            self.assertEqual(bd['f3.f1'], 'F3.1')

        with self.subTest('%s set_existing_item' % test_name):
            bd['f3.f2'] = 'foobar'
            self.assertEqual(bd['f3.f2'], 'foobar')

        with self.subTest('%s set_new_item' % test_name):
            bd['f3.f3'] = 'snafu'
            self.assertEqual(bd['f3.f3'], 'snafu')

        with self.subTest('%s get_attr' % test_name):
            self.assertEqual(bd.f3.f1, 'F3.1')

        with self.subTest('%s del' % test_name):
            tmp_len = len(bd.f3)
            del bd['f3.f2']
            self.assertEqual(len(bd), 3)
            self.assertEqual(len(bd.f3), tmp_len-1)

        with self.subTest('%s get' % test_name):
            self.assertEqual(bd.get('f3.f1'), 'F3.1')

        with self.subTest('%s get_empty' % test_name):
            self.assertEqual(bd.get('f3.bar'), None)

        with self.subTest('%s update' % test_name):
            test_dict2 = {'f4': 'F4', 'f5': {'f1':'F5.1','f2': 'F5.2'}}
            bd.update(test_dict2)
            self.assertEqual(bd['f5.f2'], 'F5.2')

    def test_3_level_dict(self):
        test_name = 'base test'
        test_dict = {'f1': 'F1',
                     'f2': 'F2',
                     'f3': {'f1': 'F3.1',
                            'f2': 'F3.2',
                            'f3': {'f1':'F3.3.1',
                                   'f2': 'F3.3.2'}}}
        bd = BaseDict(test_dict)

        with self.subTest('%s get_item' % test_name):
            self.assertEqual(bd['f3.f3.f2'], 'F3.3.2')

        with self.subTest('%s set_existing_item' % test_name):
            bd['f3.f3.f2'] = 'foobar'
            self.assertEqual(bd['f3.f3.f2'], 'foobar')

        with self.subTest('%s set_new_item' % test_name):
            bd['f3.f3.f4'] = 'snafu'
            self.assertEqual(bd['f3.f3.f4'], 'snafu')

        with self.subTest('%s get_attr' % test_name):
            self.assertEqual(bd.f3.f3.f1, 'F3.3.1')

        with self.subTest('%s del' % test_name):
            del bd['f3.f3.f2']
            self.assertEqual(len(bd), 3)
            self.assertEqual(len(bd.f3), 3)
            self.assertEqual(len(bd.f3.f3), 2)

        with self.subTest('%s get' % test_name):
            self.assertEqual(bd.get('f3.f3.f1'), 'F3.3.1')

        with self.subTest('%s get_empty' % test_name):
            self.assertEqual(bd.get('f3.f3.bar'), None)

        with self.subTest('%s update' % test_name):
            test_dict2 = {'f4': 'F4', 'f3.f3': {'f1': 'B3.3.1', 'f5': 'F3.3.5'}}
            bd.update(test_dict2)
            self.assertEqual(bd['f3.f3.f1'], 'B3.3.1')
            self.assertEqual(bd['f3.f3.f5'], 'F3.3.5')

    def test_dict_list_dict(self):
        test_name = 'base test'
        test_dict = {'f1': 'F1',
                     'f2': 'F2',
                     'f3': [
                         {'f1': 'F3.0.1', 'f2': 'F3.0.2'},
                         {'f1': 'F3.1.1', 'f2': 'F3.1.2'},
                         {'f1': 'F3.2.1', 'f2': 'F3.2.2'}],
                     'f4': ['F4.0', 'F4.1', 'F4.2']}
        bd = BaseDict(test_dict)

        with self.subTest('%s get_item' % test_name):
            self.assertEqual(bd['f3.0.f2'], 'F3.0.2')

        with self.subTest('%s set_existing_item' % test_name):
            bd['f3.2.f2'] = 'foobar'
            self.assertEqual(bd['f3.2.f2'], 'foobar')

        with self.subTest('%s set_new_item' % test_name):
            bd['f3.1.f4'] = 'snafu'
            self.assertEqual(bd['f3.1.f4'], 'snafu')

        with self.subTest('%s get_attr' % test_name):
            self.assertEqual(bd.f3[1].f1, 'F3.1.1')

        with self.subTest('%s del' % test_name):
            bd_len = len(bd)
            bd_f3_len = len(bd.f3)
            bd_f3_0_len = len(bd.f3[0])
            del bd['f3.0.f2']
            self.assertEqual(len(bd), bd_len)
            self.assertEqual(len(bd.f3), bd_f3_len)
            self.assertEqual(len(bd.f3[0]), bd_f3_0_len-1)

        with self.subTest('%s get' % test_name):
            self.assertEqual(bd.get('f3.0.f1'), 'F3.0.1')

        with self.subTest('%s get_empty' % test_name):
            self.assertEqual(bd.get('f3.0.bar'), None)

        with self.subTest('%s update' % test_name):
            test_dict2 = {'f5': 'F5', 'f3.0.f3': {'f1': 'B3.3.1', 'f5': 'F3.3.5'}}
            bd.update(test_dict2)
            self.assertEqual(bd['f3.0.f1'], 'F3.0.1')
            self.assertEqual(bd['f5'], 'F5')

        with self.subTest('%s simple_get_item' % test_name):
            self.assertEqual(bd['f4.0'], 'F4.0')

        with self.subTest('%s simple_set_existing_item' % test_name):
            bd['f4.2'] = 'B4.2'
            self.assertEqual(bd['f4'][2], 'B4.2')

        with self.subTest('%s simple_del' % test_name):
            bd_len = len(bd)
            bd_f4_len = len(bd.f4)
            del bd['f4.2']
            self.assertEqual(len(bd), bd_len)
            self.assertEqual(len(bd.f4), bd_f4_len-1)

        with self.subTest('%s append' % test_name):
            tmp_len = len(bd.f4)
            bd.f4.append('F4.3')
            self.assertEqual(tmp_len+1, len(bd.f4))

        with self.subTest('%s insert' % test_name):
            tmp_len = len(bd.f4)
            bd.f4.insert(1, 'F4.4')
            self.assertEqual(tmp_len + 1, len(bd.f4))
            self.assertEqual(bd.f4[1], 'F4.4')

        with self.subTest('%s extend' % test_name):
            tmp_ext = [{'f1': 'F3.4.1', 'f2': 'F3.4.2'}, {'f1': 'F3.5.1', 'f2': 'F3.5.2'}]
            bd.f3.extend(tmp_ext)
            self.assertEqual(bd['f3.3.f2'], 'F3.4.2')
            self.assertTrue(isinstance(bd['f3'][2], BaseDict))

        with self.subTest('%s slice' % test_name):
            tmp_slice = bd.f3[1:3]
            self.assertEqual(len(tmp_slice), 2)
            self.assertTrue(isinstance(tmp_slice, BaseList))

        with self.subTest('%s slice text' % test_name):
            tmp_slice = bd['f3.1:3']
            self.assertEqual(len(tmp_slice), 2)
            self.assertTrue(isinstance(tmp_slice, BaseList))

        # =========================================================
        q_dict = {'B1': 'B1', 'b2': 'B2'}
        q_list = ['1', 2, 3]

        with self.subTest('%s set_existing_item_check_class' % test_name):
            bd['f3.2'] = q_dict
            self.assertTrue(isinstance(bd['f3.2'], BaseDict))
            bd['f3.2'] = q_list
            self.assertTrue(isinstance(bd['f3.2'], BaseList))

        with self.subTest('%s append_check_class' % test_name):
            bd.f4.append(q_dict)
            self.assertTrue(isinstance(bd['f4'][-1], BaseDict))
            bd.f4.append(q_list)
            self.assertTrue(isinstance(bd['f4.-1'], BaseList))

        with self.subTest('%s insert_check_class' % test_name):
            bd.f4.insert(1, q_dict)
            self.assertTrue(isinstance(bd['f4.1'], BaseDict))
            bd.f4.insert(1, q_list)
            self.assertTrue(isinstance(bd['f4.1'], BaseList))

        with self.subTest('%s extend_check_class' % test_name):
            bd.f4.extend([q_dict, q_dict])
            self.assertIsInstance(bd['f4'][-1], BaseDict)
            bd.f4.append([q_list, q_list])
            self.assertIsInstance(bd['f4.-1'], BaseList)


class TestKeysandIterator(TestCase):

    def setUp(self):

        test_dict = {'f1': 'F1',
                     'f2': 'F2',
                     'f3': [
                         {'f1': 'F3.0.1', 'num': '123'},
                         {'f1': 'F3.1.1', 'num': '456'},
                         {'f1': 'F3.2.1', 'f2': 'F3.2.2', 'num': '789'}],
                     'f4': ['10', '20', '30']}
        self.bd = BaseDict(test_dict)

    def test_check_keys(self):
        keys_response = self.bd.keys()
        keys_expected = ['f1', 'f2', 'f3', 'f4']
        self.assertCountEqual(keys_expected, keys_response)

    def test_check_list_keys_full_path(self):
        keys_response = self.bd.f3.keys(return_as=self.bd.FULL_PATH)
        keys_expected = [0, 1, 2]
        self.assertCountEqual(keys_expected, keys_response)

    def test_check_list_dict_keys_full_path(self):
        keys_response = self.bd.f3[0].keys(return_as=self.bd.FULL_PATH)
        keys_expected = ['f1', 'num']
        self.assertCountEqual(keys_expected, keys_response)

    def test_check_keys_full_path_skip_list(self):
        keys_response = self.bd.f3[0].keys(return_as=self.bd.FIELD)
        keys_expected = ['f1', 'num']
        self.assertCountEqual(keys_expected, keys_response)

    def test_check_recursive_field_path(self):
        keys_response = self.bd.keys(return_as=self.bd.FIELD_PATH, recursive=True, scan_all=False)
        keys_expected = ['f1', 'f2', 'f3.f1', 'f3.num', 'f4']
        self.assertCountEqual(keys_expected, keys_response)

    def test_check_recursive_full_path(self):
        keys_response = self.bd.keys(return_as=self.bd.FULL_PATH, recursive=True, scan_all=False)
        keys_expected = ['f1', 'f2', 'f3.0.f1', 'f3.0.num', 'f3.1.f1', 'f3.1.num', 'f3.2.f1', 'f3.2.f2', 'f3.2.num',
                         'f4.0', 'f4.1', 'f4.2']
        self.assertCountEqual(keys_expected, keys_response)

    def test_check_recursive_full_path_scan_all(self):
        keys_response = self.bd.keys(return_as=self.bd.FIELD_PATH, recursive=True)
        keys_expected = ['f1', 'f2', 'f3.f1', 'f3.f2', 'f3.num', 'f4']
        self.assertCountEqual(keys_expected, keys_response)

    def test_check_recursive_full_path_scan_all_filter(self):
        keys_response = self.bd.keys(return_as=self.bd.FIELD_PATH, recursive=True, filters='*f1')
        keys_expected = ['f1', 'f3.f1']
        self.assertCountEqual(keys_expected, keys_response)

    def test_check_recursive_full_path_scan_all_filter_2(self):
        keys_response = self.bd.keys(return_as=self.bd.FULL_PATH, recursive=True, filters='*f1')
        keys_expected = ['f1', 'f3.0.f1', 'f3.1.f1', 'f3.2.f1']
        self.assertCountEqual(keys_expected, keys_response)

    def test_check_recursive_full_path_scan_all_filter_3(self):
        keys_response = self.bd.keys(return_as=self.bd.FIELD_PATH, recursive=True, filters='f2')
        keys_expected = ['f2']
        self.assertCountEqual(keys_expected, keys_response)

    def test_check_recursive_full_path_scan_all_filter_4(self):
        keys_response = self.bd.keys(return_as=self.bd.FULL_PATH, recursive=True, filters='f3*')
        keys_expected = ['f3.0.f1', 'f3.0.num', 'f3.1.f1', 'f3.1.num', 'f3.2.f1', 'f3.2.f2', 'f3.2.num']
        self.assertCountEqual(keys_expected, keys_response)

    def test_check_recursive_full_path_scan_all_filter_5(self):
        keys_response = self.bd.keys(return_as=self.bd.FIELD_PATH, recursive=True, filters='f3.num')
        keys_expected = ['f3.num']
        self.assertCountEqual(keys_expected, keys_response)

    def test_conversion_test_no_kwargs(self):
        tmp_count = self.bd.convert(conversion_fixture, 'f3.num')
        self.assertEqual(self.bd['f3.0.num'], '123-C')
        self.assertEqual(self.bd['f3.1.num'], '456-C')
        self.assertEqual(self.bd['f3.2.num'], '789-C')
        self.assertEqual(tmp_count, 3)

    def test_conversion_test_with_args(self):
        tmp_count = self.bd.convert(conversion_fixture, 'f3.num', conversion_type='int')
        self.assertEqual(self.bd['f3.0.num'], 123)
        self.assertEqual(self.bd['f3.1.num'], 456)
        self.assertEqual(self.bd['f3.2.num'], 789)
        self.assertEqual(tmp_count, 3)

    def test_run_test_with_no_args(self):
        test_expected = ['123', '456', '789']
        test_resp = self.bd.run(run_fixture, 'f3.num')
        self.assertCountEqual(test_expected, test_resp)

    def test_conversion_test_simple_list_with_args(self):
        tmp_count = self.bd.convert(conversion_fixture, 'f4', conversion_type='int')
        self.assertEqual(self.bd['f4.0'], 10)
        self.assertEqual(self.bd['f4.1'], 20)
        self.assertEqual(self.bd['f4.2'], 30)
        self.assertEqual(tmp_count, 3)

    def test_run_test_simple_list_with_no_args(self):
        test_expected = ['10', '20', '30']
        test_resp = self.bd.run(run_fixture, 'f4')
        self.assertCountEqual(test_expected, test_resp)

    def test_run_test_with_args(self):
        test_expected = [{'value': '123'}, {'value': '456'}, {'value': '789'}]
        test_resp = self.bd.run(run_fixture, 'f3.num', in_dict=True)
        self.assertCountEqual(test_expected, test_resp)

    def test_iterate_items_local(self):

        test_dict = {
            'f1': 'F1',
            'f2': 'F2',
            'f3': self.bd['f3'],
            'f4': self.bd['f4']}

        for key, item in self.bd.items():
            with self.subTest(key):
                self.assertIn(key, test_dict)
                self.assertEqual(item, test_dict[key])
                test_dict.pop(key)
        with self.subTest('all gone'):
            self.assertEqual(len(test_dict), 0)

    def test_iterate_items_recursive_hide_list(self):
        test_dict = {
            'f1': ('f1', 'F1'),
            'f2': ('f2', 'F2'),
            'f3.0.f1': ('f3.f1', 'F3.0.1'),
            'f3.0.num': ('f3.num', '123'),
            'f3.1.f1': ('f3.f1', 'F3.1.1'),
            'f3.1.num': ('f3.num', '456'),
            'f3.2.f1': ('f3.f1', 'F3.2.1'),
            'f3.2.f2': ('f3.f2', 'F3.2.2'),
            'f3.2.num': ('f3.num', '789'),
            'f4.0': ('f4', '10'),
            'f4.1': ('f4', '20'),
            'f4.2': ('f4', '30')}

        for item in self.bd.items(recursive=True, return_as=self.bd.VIEW_OBJ):
            with self.subTest(item.full_path):
                tmp_test_item = test_dict[item.full_path]
                self.assertEqual(item.field_path, tmp_test_item[0])
                self.assertEqual(item.item, tmp_test_item[1])


    def test_iterate_items_recursive_show_list(self):
        test_dict = {
            'f1': 'F1',
            'f2': 'F2',
            'f3.0.f1': 'F3.0.1',
            'f3.0.num': '123',
            'f3.1.f1': 'F3.1.1',
            'f3.1.num': '456',
            'f3.2.f1': 'F3.2.1',
            'f3.2.f2': 'F3.2.2',
            'f3.2.num': '789',
            'f4.0': '10',
            'f4.1': '20',
            'f4.2': '30'}

        tmp_items = self.bd.items(recursive=True)
        tmp_set = tmp_items[0]
        for key, item in tmp_items:
            with self.subTest(key):
                self.assertIn(key, test_dict)
                self.assertEqual(item, test_dict[key])
                test_dict.pop(key)
        with self.subTest('all gone'):
            self.assertEqual(len(test_dict), 0)


class TestDictandListBaseFunctions(TestCase):
    def setUp(self):
        test_dict = {'f1': 'F1',
                     'f2': 'F2',
                     'f3': [
                         {'f1': 'F3.0.1', 'num': '123'},
                         {'f1': 'F3.1.1', 'num': '456'},
                         {'f1': 'F3.2.1', 'f2': 'F3.2.2', 'num': '789'}],
                     'f4': ['10', '20', '30']}
        test_dict3 = {'f1': 'F1_diff',
                     'f2': 'F2',
                     'f3': [
                         {'f1': 'F3.0.1', 'num': '123'},
                         {'f1': 'F3.1.1', 'num': '456'},
                         {'f1': 'F3.2.1', 'f2': 'F3.2.2', 'num': '789'}],
                     'f4': ['10', '20', '30']}
        test_dict4 = {'f1': 'F1',
                      'f2': 'F2',
                      'f3': [
                          {'f1': 'F3.0.1_diff', 'num': '123'},
                          {'f1': 'F3.1.1', 'num': '456'},
                          {'f1': 'F3.2.1', 'f2': 'F3.2.2', 'num': '789'}],
                      'f4': ['10', '20', '30']}

        self.bd1 = BaseDict(test_dict, hash_field='f1')
        self.bd2 = BaseDict(test_dict)
        self.bd3 = BaseDict(test_dict3)
        self.bd4 = BaseDict(test_dict4)

        test_list = [
            {'f1': 'F3.0.1', 'num': {'value': '123'}},
            {'f1': 'F3.1.1', 'num': {'value': '456'}},
            {'f1': 'F3.2.1', 'f2': 'F3.2.2', 'num': {'value': '789'}}]
        test_list3 = [
            {'f1': 'F3.0.1_diff', 'num': {'value': '123'}},
            {'f1': 'F3.1.1', 'num': {'value': '456'}},
            {'f1': 'F3.2.1', 'f2': 'F3.2.2', 'num': {'value': '789'}}]
        test_list4 = [
            {'f1': 'F3.0.1', 'num': {'value': '123_diff'}},
            {'f1': 'F3.1.1', 'num': {'value': '456'}},
            {'f1': 'F3.2.1', 'f2': 'F3.2.2', 'num': {'value': '789'}}]
        self.bl1 = BaseList(test_list, hash_field='f1')
        self.bl2 = BaseList(test_list)
        self.bl3 = BaseList(test_list3)
        self.bl4 = BaseList(test_list4)

    def test_equal_base_dict(self):
        self.assertEqual(self.bd1, self.bd2)

    def test_not_equal_base_dict(self):
        self.assertNotEqual(self.bd2, self.bd3)

    def test_not_equal_sub_dict(self):
        self.assertNotEqual(self.bd1, self.bd4)

    def test_equal_base_list(self):
        self.assertEqual(self.bl1, self.bl2)

    def test_not_equal_sub_list(self):
        self.assertNotEqual(self.bl2, self.bl3)

    def test_not_equal_sub_sub_list(self):
        self.assertNotEqual(self.bl1, self.bl4)

    def test_in_dict(self):
        self.assertIn('f3.num', self.bd1)
        self.assertIn('f3.0.num', self.bd1)
        self.assertIn('f3.0', self.bd1)
        self.assertIn('f4.2', self.bd1)

        self.assertNotIn('f6.num', self.bd1)
        self.assertNotIn('num', self.bd1)
        self.assertNotIn(4, self.bd1)
        self.assertNotIn('blah', self.bd1)

    def test_in_list(self):
        self.assertIn(0, self.bl1)
        self.assertIn('0.num', self.bl1)
        self.assertIn('num', self.bl1)
        self.assertIn('num.value', self.bl1)

        self.assertNotIn(10, self.bl1)
        self.assertNotIn('blah', self.bl1)
        self.assertNotIn('value', self.bl1)

    def test_hash_list(self):
        tmp_hash = hash(self.bl1)

    def test_hash_dict(self):
        tmp_hash = hash(self.bd1)

    def test_clear_list(self):
        self.assertEqual(len(self.bl4), 3)
        self.assertTrue(self.bl4)
        self.bl4.clear()
        self.assertEqual(len(self.bl4), 0)
        self.assertFalse(self.bl4)

    def test_clear_dict(self):
        self.assertEqual(len(self.bd4), 4)
        self.assertTrue(self.bd4)
        self.bd4.clear()
        self.assertEqual(len(self.bd4), 0)
        self.assertFalse(self.bd4)

