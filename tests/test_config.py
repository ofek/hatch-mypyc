# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import pytest
from hatchling.builders.config import BuilderConfig

from hatch_mypyc.plugin import MypycBuildHook


class TestMypyArgs:
    def test_correct(self, new_project):
        config = {'mypy-args': ['foo']}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        assert build_hook.config_mypy_args == ['foo']

    def test_not_array(self, new_project):
        config = {'mypy-args': 9000}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        with pytest.raises(TypeError, match='Option `mypy-args` for build hook `mypyc` must be an array'):
            _ = build_hook.config_mypy_args

    def test_argument_not_string(self, new_project):
        config = {'mypy-args': [9000]}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        with pytest.raises(
            TypeError, match='Argument #1 of option `mypy-args` for build hook `mypyc` must be a string'
        ):
            _ = build_hook.config_mypy_args

    def test_argument_empty_string(self, new_project):
        config = {'mypy-args': ['']}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        with pytest.raises(
            ValueError, match='Argument #1 of option `mypy-args` for build hook `mypyc` cannot be an empty string'
        ):
            _ = build_hook.config_mypy_args


class TestOptions:
    def test_correct(self, new_project):
        config = {'options': {'opt_level': '3'}}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        assert build_hook.config_options == {'opt_level': '3'}

    def test_not_table(self, new_project):
        config = {'options': 9000}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        with pytest.raises(TypeError, match='Option `options` for build hook `mypyc` must be a table'):
            _ = build_hook.config_options


class TestInclude:
    def test_correct(self, new_project):
        config = {'include': ['foo']}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        assert build_hook.config_include == ['foo']

    def test_not_array(self, new_project):
        config = {'include': 9000}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        with pytest.raises(TypeError, match='Option `include` for build hook `mypyc` must be an array'):
            _ = build_hook.config_include

    def test_pattern_not_string(self, new_project):
        config = {'include': [9000]}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        with pytest.raises(TypeError, match='Pattern #1 of option `include` for build hook `mypyc` must be a string'):
            _ = build_hook.config_include

    def test_pattern_empty_string(self, new_project):
        config = {'include': ['']}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        with pytest.raises(
            ValueError, match='Pattern #1 of option `include` for build hook `mypyc` cannot be an empty string'
        ):
            _ = build_hook.config_include


class TestExclude:
    def test_correct(self, new_project):
        config = {'exclude': ['foo']}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        assert build_hook.config_exclude == ['foo']

    def test_not_array(self, new_project):
        config = {'exclude': 9000}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        with pytest.raises(TypeError, match='Option `exclude` for build hook `mypyc` must be an array'):
            _ = build_hook.config_exclude

    def test_pattern_not_string(self, new_project):
        config = {'exclude': [9000]}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        with pytest.raises(TypeError, match='Pattern #1 of option `exclude` for build hook `mypyc` must be a string'):
            _ = build_hook.config_exclude

    def test_pattern_empty_string(self, new_project):
        config = {'exclude': ['']}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, None, None, str(build_dir), 'wheel')

        with pytest.raises(
            ValueError, match='Pattern #1 of option `exclude` for build hook `mypyc` cannot be an empty string'
        ):
            _ = build_hook.config_exclude


class TestPatternMatching:
    def test_no_include(self, new_project):
        build_dir = new_project / 'dist'
        config = {}
        target_config = {}
        build_config = BuilderConfig(None, str(new_project), 'wheel', {}, target_config)
        build_hook = MypycBuildHook(str(new_project), config, build_config, None, str(build_dir), 'wheel')

        with pytest.raises(ValueError, match='Option `include` for build hook `mypyc` is required'):
            build_hook.include_path('foo/bar.py')

    def test_default_include(self, new_project):
        build_dir = new_project / 'dist'
        config = {}
        target_config = {'include': ['foo']}
        build_config = BuilderConfig(None, str(new_project), 'wheel', {}, target_config)
        build_hook = MypycBuildHook(str(new_project), config, build_config, None, str(build_dir), 'wheel')

        assert build_hook.include_path('foo/bar.py')
        assert build_hook.include_path('foo/baz.py')
        assert not build_hook.include_path('bar/foo.py')
        assert not build_hook.include_path('bar/baz.py')

    def test_default_include_packages(self, new_project):
        build_dir = new_project / 'dist'
        config = {}
        target_config = {'packages': ['foo']}
        build_config = BuilderConfig(None, str(new_project), 'wheel', {}, target_config)
        build_hook = MypycBuildHook(str(new_project), config, build_config, None, str(build_dir), 'wheel')

        assert build_hook.include_path('foo/bar.py')
        assert build_hook.include_path('foo/baz.py')
        assert not build_hook.include_path('bar/foo.py')
        assert not build_hook.include_path('bar/baz.py')

    def test_include(self, new_project):
        build_dir = new_project / 'dist'
        config = {'include': ['bar']}
        target_config = {'include': ['foo']}
        build_config = BuilderConfig(None, str(new_project), 'wheel', {}, target_config)
        build_hook = MypycBuildHook(str(new_project), config, build_config, None, str(build_dir), 'wheel')

        assert not build_hook.include_path('foo/bar.py')
        assert not build_hook.include_path('foo/baz.py')
        assert build_hook.include_path('bar/foo.py')
        assert build_hook.include_path('bar/baz.py')

    def test_default_exclude(self, new_project):
        build_dir = new_project / 'dist'
        config = {'include': ['bar']}
        target_config = {'include': ['foo'], 'exclude': ['foo.py']}
        build_config = BuilderConfig(None, str(new_project), 'wheel', {}, target_config)
        build_hook = MypycBuildHook(str(new_project), config, build_config, None, str(build_dir), 'wheel')

        assert not build_hook.include_path('foo/bar.py')
        assert not build_hook.include_path('foo/baz.py')
        assert not build_hook.include_path('bar/foo.py')
        assert build_hook.include_path('bar/baz.py')

    def test_exclude(self, new_project):
        build_dir = new_project / 'dist'
        config = {'include': ['bar'], 'exclude': ['baz.py']}
        target_config = {'include': ['foo'], 'exclude': ['foo.py']}
        build_config = BuilderConfig(None, str(new_project), 'wheel', {}, target_config)
        build_hook = MypycBuildHook(str(new_project), config, build_config, None, str(build_dir), 'wheel')

        assert not build_hook.include_path('foo/bar.py')
        assert not build_hook.include_path('foo/baz.py')
        assert build_hook.include_path('bar/foo.py')
        assert not build_hook.include_path('bar/baz.py')


class TestPackageSource:
    def test_none(self, new_project):
        build_dir = new_project / 'dist'
        config = {}
        target_config = {'packages': ['foo']}
        build_config = BuilderConfig(None, str(new_project), 'wheel', {}, target_config)
        build_hook = MypycBuildHook(str(new_project), config, build_config, None, str(build_dir), 'wheel')

        assert build_hook.package_source == ''

    def test_correct(self, new_project):
        build_dir = new_project / 'dist'
        config = {}
        target_config = {'packages': ['src/foo']}
        build_config = BuilderConfig(None, str(new_project), 'wheel', {}, target_config)
        build_hook = MypycBuildHook(str(new_project), config, build_config, None, str(build_dir), 'wheel')

        assert build_hook.package_source == 'src'


def test_coverage(new_project):
    build_config = BuilderConfig(None, str(new_project), 'wheel', {}, {'include': ['foo']})
    build_hook = MypycBuildHook(str(new_project), {}, build_config, None, str(new_project / 'dist'), 'wheel')

    assert build_hook.config_mypy_args is build_hook.config_mypy_args
    assert build_hook.config_options is build_hook.config_options
    assert build_hook.config_include is build_hook.config_include
    assert build_hook.config_exclude is build_hook.config_exclude
    assert build_hook.package_source is build_hook.package_source
    assert build_hook.include_spec is build_hook.include_spec
    assert build_hook.exclude_spec is build_hook.exclude_spec
    assert build_hook.included_files is build_hook.included_files
    assert build_hook.normalized_included_files is build_hook.normalized_included_files
    assert build_hook.artifact_globs is build_hook.artifact_globs
    assert build_hook.normalized_artifact_globs is build_hook.normalized_artifact_globs
    assert build_hook.artifact_patterns is build_hook.artifact_patterns
