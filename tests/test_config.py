# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import pytest

from hatch_mypyc.plugin import MypycBuildHook


class TestMypyArgs:
    def test_correct(self, new_project):
        config = {'mypy-args': ['foo']}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        assert build_hook.config_mypy_args == ['foo']

    def test_not_array(self, new_project):
        config = {'mypy-args': 9000}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        with pytest.raises(TypeError, match='Option `mypy-args` for build hook `mypyc` must be an array'):
            _ = build_hook.config_mypy_args

    def test_argument_not_string(self, new_project):
        config = {'mypy-args': [9000]}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        with pytest.raises(
            TypeError, match='Argument #1 of option `mypy-args` for build hook `mypyc` must be a string'
        ):
            _ = build_hook.config_mypy_args

    def test_argument_empty_string(self, new_project):
        config = {'mypy-args': ['']}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        with pytest.raises(
            ValueError, match='Argument #1 of option `mypy-args` for build hook `mypyc` cannot be an empty string'
        ):
            _ = build_hook.config_mypy_args


class TestOptions:
    def test_correct(self, new_project):
        config = {'options': {'opt_level': '3'}}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        assert build_hook.config_options == {'opt_level': '3'}

    def test_not_table(self, new_project):
        config = {'options': 9000}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        with pytest.raises(TypeError, match='Option `options` for build hook `mypyc` must be a table'):
            _ = build_hook.config_options


class TestInclude:
    def test_correct(self, new_project):
        config = {'include': ['foo']}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        assert build_hook.config_include == ['foo']

    def test_not_array(self, new_project):
        config = {'include': 9000}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        with pytest.raises(TypeError, match='Option `include` for build hook `mypyc` must be an array'):
            _ = build_hook.config_include

    def test_missing(self, new_project):
        config = {'include': []}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        with pytest.raises(ValueError, match='Option `include` for build hook `mypyc` is required'):
            _ = build_hook.config_include

    def test_pattern_not_string(self, new_project):
        config = {'include': [9000]}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        with pytest.raises(TypeError, match='Pattern #1 of option `include` for build hook `mypyc` must be a string'):
            _ = build_hook.config_include

    def test_pattern_empty_string(self, new_project):
        config = {'include': ['']}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        with pytest.raises(
            ValueError, match='Pattern #1 of option `include` for build hook `mypyc` cannot be an empty string'
        ):
            _ = build_hook.config_include


class TestExclude:
    def test_correct(self, new_project):
        config = {'exclude': ['foo']}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        assert build_hook.config_exclude == ['foo']

    def test_not_array(self, new_project):
        config = {'exclude': 9000}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        with pytest.raises(TypeError, match='Option `exclude` for build hook `mypyc` must be an array'):
            _ = build_hook.config_exclude

    def test_pattern_not_string(self, new_project):
        config = {'exclude': [9000]}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        with pytest.raises(TypeError, match='Pattern #1 of option `exclude` for build hook `mypyc` must be a string'):
            _ = build_hook.config_exclude

    def test_pattern_empty_string(self, new_project):
        config = {'exclude': ['']}
        build_dir = new_project / 'dist'
        build_hook = MypycBuildHook(str(new_project), config, str(build_dir), 'wheel')

        with pytest.raises(
            ValueError, match='Pattern #1 of option `exclude` for build hook `mypyc` cannot be an empty string'
        ):
            _ = build_hook.config_exclude
