import unittest
from pyramid.testing import cleanUp

class TestAssetsConfiguratorMixin(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.config import Configurator
        config = Configurator(*arg, **kw)
        return config

    def test_override_asset_samename(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.override_asset,'a', 'a')

    def test_override_asset_directory_with_file(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.override_asset,
                          'a:foo/', 'a:foo.pt')

    def test_override_asset_file_with_directory(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.override_asset,
                          'a:foo.pt', 'a:foo/')

    def test_override_asset_file_with_package(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.override_asset,
                          'a:foo.pt', 'a')

    def test_override_asset_file_with_file(self):
        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'pyramid.tests.test_config.pkgs.asset:templates/foo.pt',
            'pyramid.tests.test_config.pkgs.asset.subpackage:templates/bar.pt',
            _override=override)
        from pyramid.tests.test_config.pkgs import asset
        from pyramid.tests.test_config.pkgs.asset import subpackage
        self.assertEqual(override.package, asset)
        self.assertEqual(override.path, 'templates/foo.pt')
        self.assertEqual(override.override_package, subpackage)
        self.assertEqual(override.override_prefix, 'templates/bar.pt')

    def test_override_asset_package_with_package(self):
        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'pyramid.tests.test_config.pkgs.asset',
            'pyramid.tests.test_config.pkgs.asset.subpackage',
            _override=override)
        from pyramid.tests.test_config.pkgs import asset
        from pyramid.tests.test_config.pkgs.asset import subpackage
        self.assertEqual(override.package, asset)
        self.assertEqual(override.path, '')
        self.assertEqual(override.override_package, subpackage)
        self.assertEqual(override.override_prefix, '')

    def test_override_asset_directory_with_directory(self):
        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'pyramid.tests.test_config.pkgs.asset:templates/',
            'pyramid.tests.test_config.pkgs.asset.subpackage:templates/',
            _override=override)
        from pyramid.tests.test_config.pkgs import asset
        from pyramid.tests.test_config.pkgs.asset import subpackage
        self.assertEqual(override.package, asset)
        self.assertEqual(override.path, 'templates/')
        self.assertEqual(override.override_package, subpackage)
        self.assertEqual(override.override_prefix, 'templates/')

    def test_override_asset_directory_with_package(self):
        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'pyramid.tests.test_config.pkgs.asset:templates/',
            'pyramid.tests.test_config.pkgs.asset.subpackage',
            _override=override)
        from pyramid.tests.test_config.pkgs import asset
        from pyramid.tests.test_config.pkgs.asset import subpackage
        self.assertEqual(override.package, asset)
        self.assertEqual(override.path, 'templates/')
        self.assertEqual(override.override_package, subpackage)
        self.assertEqual(override.override_prefix, '')

    def test_override_asset_package_with_directory(self):
        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'pyramid.tests.test_config.pkgs.asset',
            'pyramid.tests.test_config.pkgs.asset.subpackage:templates/',
            _override=override)
        from pyramid.tests.test_config.pkgs import asset
        from pyramid.tests.test_config.pkgs.asset import subpackage
        self.assertEqual(override.package, asset)
        self.assertEqual(override.path, '')
        self.assertEqual(override.override_package, subpackage)
        self.assertEqual(override.override_prefix, 'templates/')

    def test__override_not_yet_registered(self):
        from pyramid.interfaces import IPackageOverrides
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        config = self._makeOne()
        config._override(package, 'path', opackage, 'oprefix',
                         PackageOverrides=DummyPackageOverrides)
        overrides = config.registry.queryUtility(IPackageOverrides,
                                                 name='package')
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])
        self.assertEqual(overrides.package, package)

    def test__override_already_registered(self):
        from pyramid.interfaces import IPackageOverrides
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        overrides = DummyPackageOverrides(package)
        config = self._makeOne()
        config.registry.registerUtility(overrides, IPackageOverrides,
                                        name='package')
        config._override(package, 'path', opackage, 'oprefix',
                         PackageOverrides=DummyPackageOverrides)
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])
        self.assertEqual(overrides.package, package)


class TestOverrideProvider(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from pyramid.config.assets import OverrideProvider
        return OverrideProvider

    def _makeOne(self, module):
        klass = self._getTargetClass()
        return klass(module)

    def _registerOverrides(self, overrides, name='pyramid.tests.test_config'):
        from pyramid.interfaces import IPackageOverrides
        from pyramid.threadlocal import get_current_registry
        reg = get_current_registry()
        reg.registerUtility(overrides, IPackageOverrides, name=name)

    def test_get_resource_filename_no_overrides(self):
        import os
        resource_name = 'test_assets.py'
        import pyramid.tests.test_config
        provider = self._makeOne(pyramid.tests.test_config)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = os.path.join(here, resource_name)
        result = provider.get_resource_filename(None, resource_name)
        self.assertEqual(result, expected)

    def test_get_resource_stream_no_overrides(self):
        import os
        resource_name = 'test_assets.py'
        import pyramid.tests.test_config
        provider = self._makeOne(pyramid.tests.test_config)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, resource_name)).read()
        result = provider.get_resource_stream(None, resource_name)
        self.assertEqual(result.read().replace('\r', ''), expected)

    def test_get_resource_string_no_overrides(self):
        import os
        resource_name = 'test_assets.py'
        import pyramid.tests.test_config
        provider = self._makeOne(pyramid.tests.test_config)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, resource_name)).read()
        result = provider.get_resource_string(None, resource_name)
        self.assertEqual(result.replace('\r', ''), expected)

    def test_has_resource_no_overrides(self):
        resource_name = 'test_assets.py'
        import pyramid.tests.test_config
        provider = self._makeOne(pyramid.tests.test_config)
        result = provider.has_resource(resource_name)
        self.assertEqual(result, True)

    def test_resource_isdir_no_overrides(self):
        file_resource_name = 'test_assets.py'
        directory_resource_name = 'files'
        import pyramid.tests.test_config
        provider = self._makeOne(pyramid.tests.test_config)
        result = provider.resource_isdir(file_resource_name)
        self.assertEqual(result, False)
        result = provider.resource_isdir(directory_resource_name)
        self.assertEqual(result, True)

    def test_resource_listdir_no_overrides(self):
        resource_name = 'files'
        import pyramid.tests.test_config
        provider = self._makeOne(pyramid.tests.test_config)
        result = provider.resource_listdir(resource_name)
        self.assertTrue(result)

    def test_get_resource_filename_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        import os
        resource_name = 'test_assets.py'
        import pyramid.tests.test_config
        provider = self._makeOne(pyramid.tests.test_config)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = os.path.join(here, resource_name)
        result = provider.get_resource_filename(None, resource_name)
        self.assertEqual(result, expected)
        
    def test_get_resource_stream_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        import os
        resource_name = 'test_assets.py'
        import pyramid.tests.test_config
        provider = self._makeOne(pyramid.tests.test_config)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, resource_name)).read()
        result = provider.get_resource_stream(None, resource_name)
        self.assertEqual(result.read(), expected)

    def test_get_resource_string_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        import os
        resource_name = 'test_assets.py'
        import pyramid.tests.test_config
        provider = self._makeOne(pyramid.tests.test_config)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, resource_name)).read()
        result = provider.get_resource_string(None, resource_name)
        self.assertEqual(result, expected)

    def test_has_resource_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        resource_name = 'test_assets.py'
        import pyramid.tests.test_config
        provider = self._makeOne(pyramid.tests.test_config)
        result = provider.has_resource(resource_name)
        self.assertEqual(result, True)

    def test_resource_isdir_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        resource_name = 'files'
        import pyramid.tests.test_config
        provider = self._makeOne(pyramid.tests.test_config)
        result = provider.resource_isdir(resource_name)
        self.assertEqual(result, True)

    def test_resource_listdir_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        resource_name = 'files'
        import pyramid.tests.test_config
        provider = self._makeOne(pyramid.tests.test_config)
        result = provider.resource_listdir(resource_name)
        self.assertTrue(result)

    def test_get_resource_filename_override_returns_value(self):
        overrides = DummyOverrides('value')
        import pyramid.tests.test_config
        self._registerOverrides(overrides)
        provider = self._makeOne(pyramid.tests.test_config)
        result = provider.get_resource_filename(None, 'test_assets.py')
        self.assertEqual(result, 'value')

    def test_get_resource_stream_override_returns_value(self):
        overrides = DummyOverrides('value')
        import pyramid.tests.test_config
        self._registerOverrides(overrides)
        provider = self._makeOne(pyramid.tests.test_config)
        result = provider.get_resource_stream(None, 'test_assets.py')
        self.assertEqual(result, 'value')

    def test_get_resource_string_override_returns_value(self):
        overrides = DummyOverrides('value')
        import pyramid.tests.test_config
        self._registerOverrides(overrides)
        provider = self._makeOne(pyramid.tests.test_config)
        result = provider.get_resource_string(None, 'test_assets.py')
        self.assertEqual(result, 'value')

    def test_has_resource_override_returns_True(self):
        overrides = DummyOverrides(True)
        import pyramid.tests.test_config
        self._registerOverrides(overrides)
        provider = self._makeOne(pyramid.tests.test_config)
        result = provider.has_resource('test_assets.py')
        self.assertEqual(result, True)

    def test_resource_isdir_override_returns_False(self):
        overrides = DummyOverrides(False)
        import pyramid.tests.test_config
        self._registerOverrides(overrides)
        provider = self._makeOne(pyramid.tests.test_config)
        result = provider.resource_isdir('files')
        self.assertEqual(result, False)

    def test_resource_listdir_override_returns_values(self):
        overrides = DummyOverrides(['a'])
        import pyramid.tests.test_config
        self._registerOverrides(overrides)
        provider = self._makeOne(pyramid.tests.test_config)
        result = provider.resource_listdir('files')
        self.assertEqual(result, ['a'])

class TestPackageOverrides(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.config.assets import PackageOverrides
        return PackageOverrides

    def _makeOne(self, package, pkg_resources=None):
        klass = self._getTargetClass()
        if pkg_resources is None:
            pkg_resources = DummyPkgResources()
        return klass(package, pkg_resources=pkg_resources)

    def test_ctor_package_already_has_loader_of_different_type(self):
        package = DummyPackage('package')
        package.__loader__ = True
        self.assertRaises(TypeError, self._makeOne, package)

    def test_ctor_package_already_has_loader_of_same_type(self):
        package = DummyPackage('package')
        package.__loader__ = self._makeOne(package)
        po = self._makeOne(package)
        self.assertEqual(package.__loader__, po)

    def test_ctor_sets_loader(self):
        package = DummyPackage('package')
        po = self._makeOne(package)
        self.assertEqual(package.__loader__, po)

    def test_ctor_registers_loader_type(self):
        from pyramid.config.assets import OverrideProvider
        dummy_pkg_resources = DummyPkgResources()
        package = DummyPackage('package')
        po = self._makeOne(package, dummy_pkg_resources)
        self.assertEqual(dummy_pkg_resources.registered, [(po.__class__,
                         OverrideProvider)])

    def test_ctor_sets_local_state(self):
        package = DummyPackage('package')
        po = self._makeOne(package)
        self.assertEqual(po.overrides, [])
        self.assertEqual(po.overridden_package_name, 'package')

    def test_insert_directory(self):
        from pyramid.config.assets import DirectoryOverride
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= [None]
        po.insert('foo/', 'package', 'bar/')
        self.assertEqual(len(po.overrides), 2)
        override = po.overrides[0]
        self.assertEqual(override.__class__, DirectoryOverride)

    def test_insert_file(self):
        from pyramid.config.assets import FileOverride
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= [None]
        po.insert('foo.pt', 'package', 'bar.pt')
        self.assertEqual(len(po.overrides), 2)
        override = po.overrides[0]
        self.assertEqual(override.__class__, FileOverride)

    def test_insert_emptystring(self):
        # XXX is this a valid case for a directory?
        from pyramid.config.assets import DirectoryOverride
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= [None]
        po.insert('', 'package', 'bar/')
        self.assertEqual(len(po.overrides), 2)
        override = po.overrides[0]
        self.assertEqual(override.__class__, DirectoryOverride)

    def test_search_path(self):
        overrides = [ DummyOverride(None), DummyOverride(('package', 'name'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(list(po.search_path('whatever')),
                         [('package', 'name')])

    def test_get_filename(self):
        import os
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests.test_config', 'test_assets.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        here = os.path.dirname(os.path.abspath(__file__))
        expected = os.path.join(here, 'test_assets.py')
        self.assertEqual(po.get_filename('whatever'), expected)

    def test_get_filename_file_doesnt_exist(self):
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests.test_config', 'wont_exist'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.get_filename('whatever'), None)
        
    def test_get_stream(self):
        import os
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests.test_config', 'test_assets.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, 'test_assets.py')).read()
        self.assertEqual(po.get_stream('whatever').read().replace('\r', ''),
                         expected)
        
    def test_get_stream_file_doesnt_exist(self):
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests.test_config', 'wont_exist'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.get_stream('whatever'), None)

    def test_get_string(self):
        import os
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests.test_config', 'test_assets.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, 'test_assets.py')).read()
        self.assertEqual(po.get_string('whatever').replace('\r', ''), expected)
        
    def test_get_string_file_doesnt_exist(self):
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests.test_config', 'wont_exist'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.get_string('whatever'), None)

    def test_has_resource(self):
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests.test_config', 'test_assets.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.has_resource('whatever'), True)

    def test_has_resource_file_doesnt_exist(self):
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests.test_config', 'wont_exist'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.has_resource('whatever'), None)

    def test_isdir_false(self):
        overrides = [ DummyOverride(
            ('pyramid.tests.test_config', 'test_assets.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.isdir('whatever'), False)
        
    def test_isdir_true(self):
        overrides = [ DummyOverride(
            ('pyramid.tests.test_config', 'files'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.isdir('whatever'), True)

    def test_isdir_doesnt_exist(self):
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests.test_config', 'wont_exist'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.isdir('whatever'), None)

    def test_listdir(self):
        overrides = [ DummyOverride(
            ('pyramid.tests.test_config', 'files'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertTrue(po.listdir('whatever'))

    def test_listdir_doesnt_exist(self):
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests.test_config', 'wont_exist'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.listdir('whatever'), None)

class TestDirectoryOverride(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.config.assets import DirectoryOverride
        return DirectoryOverride

    def _makeOne(self, path, package, prefix):
        klass = self._getTargetClass()
        return klass(path, package, prefix)

    def test_it_match(self):
        o = self._makeOne('foo/', 'package', 'bar/')
        result = o('foo/something.pt')
        self.assertEqual(result, ('package', 'bar/something.pt'))
        
    def test_it_no_match(self):
        o = self._makeOne('foo/', 'package', 'bar/')
        result = o('baz/notfound.pt')
        self.assertEqual(result, None)

class TestFileOverride(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.config.assets import FileOverride
        return FileOverride

    def _makeOne(self, path, package, prefix):
        klass = self._getTargetClass()
        return klass(path, package, prefix)

    def test_it_match(self):
        o = self._makeOne('foo.pt', 'package', 'bar.pt')
        result = o('foo.pt')
        self.assertEqual(result, ('package', 'bar.pt'))
        
    def test_it_no_match(self):
        o = self._makeOne('foo.pt', 'package', 'bar.pt')
        result = o('notfound.pt')
        self.assertEqual(result, None)

class DummyOverride:
    def __init__(self, result):
        self.result = result

    def __call__(self, resource_name):
        return self.result

class DummyOverrides:
    def __init__(self, result):
        self.result = result

    def get_filename(self, resource_name):
        return self.result

    listdir = isdir = has_resource = get_stream = get_string = get_filename

class DummyPackageOverrides:
    def __init__(self, package):
        self.package = package
        self.inserted = []

    def insert(self, path, package, prefix):
        self.inserted.append((path, package, prefix))
    
class DummyPkgResources:
    def __init__(self):
        self.registered = []

    def register_loader_type(self, typ, inst):
        self.registered.append((typ, inst))
        
class DummyPackage:
    def __init__(self, name):
        self.__name__ = name

class DummyUnderOverride:
    def __call__(self, package, path, override_package, override_prefix,
                 _info=u''):
        self.package = package
        self.path = path
        self.override_package = override_package
        self.override_prefix = override_prefix

