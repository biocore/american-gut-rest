from unittest import TestCase, main
import os
import tempfile


def dump_config(**kwargs):
    name = None
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as fp:
        name = fp.name
        fp.write("[main]\n")
        for item in kwargs.items():
            fp.write("%s=%s\n" % item)
    return name


class ConfigTests(TestCase):
    def setUp(self):
        import agr
        self.agr = agr
        self.to_delete = []

    def tearDown(self):
        del self.agr
        os.environ.pop('AGREST_CONFIG', None)

        for f in self.to_delete:
            os.remove(f)

    def trigger_reload(self):
        reload(self.agr)

    def test_define_an_option(self):
        changed = {'serverport': '1234'}
        os.environ['AGREST_CONFIG'] = dump_config(**changed)
        self.trigger_reload()
        self.check_config(**changed)

    def test_full_defaults(self):
        self.trigger_reload()
        self.check_config()

    def test_test_mic_check(self):
        with self.assertRaises(AssertionError):
            self.check_config(**{'serverport': 'xyz'})

    def check_config(self, **kwargs):
        self.assertEqual(self.agr.serverport,
                         kwargs.get('serverport', '8080'))
        self.assertEqual(self.agr.location_base,
                         kwargs.get('location_base', ''))
        self.assertEqual(self.agr.base_conf_dir,
                         kwargs.get('base_conf_dir', '.'))
        self.assertEqual(self.agr.db_user,
                         kwargs.get('db_user', 'postgres'))
        self.assertEqual(self.agr.db_host,
                         kwargs.get('db_host', 'localhost'))
        self.assertEqual(self.agr.db_password,
                         kwargs.get('db_password', ''))
        self.assertEqual(self.agr.db_name,
                         kwargs.get('db_name', 'ag_rest'))
        self.assertEqual(self.agr.admin_db_user,
                         kwargs.get('admin_db_user', 'postgres'))
        self.assertEqual(self.agr.admin_db_password,
                         kwargs.get('admin_db_password', ''))
        self.assertEqual(self.agr.test_environment,
                         kwargs.get('test_environment', True))

if __name__ == '__main__':
    main()
