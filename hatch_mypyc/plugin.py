# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import os
import platform
import subprocess
import sys
from functools import cached_property
from tempfile import TemporaryDirectory

import pathspec
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from .utils import construct_setup_file


class MypycBuildHook(BuildHookInterface):
    PLUGIN_NAME = 'mypyc'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._on_windows = platform.system() == 'Windows'

    @cached_property
    def config_mypy_args(self):
        mypy_args = self.config.get('mypy-args', [])
        if isinstance(mypy_args, list):
            for i, argument in enumerate(mypy_args, 1):
                if not isinstance(argument, str):
                    raise TypeError(
                        f'Argument #{i} of option `mypy-args` for build hook `{self.PLUGIN_NAME}` must be a string'
                    )
                elif not argument:
                    raise ValueError(
                        f'Argument #{i} of option `mypy-args` for build hook `{self.PLUGIN_NAME}` '
                        f'cannot be an empty string'
                    )
        else:
            raise TypeError(f'Option `mypy-args` for build hook `{self.PLUGIN_NAME}` must be an array')

        return mypy_args

    @cached_property
    def config_options(self):
        options = self.config.get('options', {})
        if not isinstance(options, dict):
            raise TypeError(f'Option `options` for build hook `{self.PLUGIN_NAME}` must be a table')

        return options

    @cached_property
    def config_include(self):
        patterns = self.config.get('include', [])
        if isinstance(patterns, list):
            if not patterns:
                raise ValueError(f'Option `include` for build hook `{self.PLUGIN_NAME}` is required')

            for i, pattern in enumerate(patterns, 1):
                if not isinstance(pattern, str):
                    raise TypeError(
                        f'Pattern #{i} of option `include` for build hook `{self.PLUGIN_NAME}` must be a string'
                    )
                elif not pattern:
                    raise ValueError(
                        f'Pattern #{i} of option `include` for build hook `{self.PLUGIN_NAME}` '
                        f'cannot be an empty string'
                    )
        else:
            raise TypeError(f'Option `include` for build hook `{self.PLUGIN_NAME}` must be an array')

        return patterns

    @cached_property
    def config_exclude(self):
        patterns = self.config.get('exclude', [])
        if isinstance(patterns, list):
            for i, pattern in enumerate(patterns, 1):
                if not isinstance(pattern, str):
                    raise TypeError(
                        f'Pattern #{i} of option `exclude` for build hook `{self.PLUGIN_NAME}` must be a string'
                    )
                elif not pattern:
                    raise ValueError(
                        f'Pattern #{i} of option `exclude` for build hook `{self.PLUGIN_NAME}` '
                        f'cannot be an empty string'
                    )
        else:
            raise TypeError(f'Option `exclude` for build hook `{self.PLUGIN_NAME}` must be an array')

        return patterns

    @cached_property
    def include_spec(self):
        return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, self.config_include)

    @cached_property
    def exclude_spec(self):
        if not self.config_exclude:
            return None

        return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, self.config_exclude)

    def include_path(self, relative_path):
        return self.include_spec.match_file(relative_path) and not self.path_is_excluded(relative_path)

    def path_is_excluded(self, relative_path):
        if self.exclude_spec is None:
            return False

        return self.exclude_spec.match_file(relative_path)

    @cached_property
    def included_files(self):
        included_files = []

        for root, dirs, files in os.walk(self.root):
            relative_path = os.path.relpath(root, self.root)

            # First iteration
            if relative_path == '.':
                relative_path = ''

            dirs[:] = sorted(
                d
                for d in dirs
                # The trailing slash is necessary so e.g. `bar/` matches `foo/bar`
                if not self.path_is_excluded('{}/'.format(os.path.join(relative_path, d)))
            )

            for f in sorted(files):
                if not f.endswith('.py'):
                    continue

                relative_file_path = os.path.join(relative_path, f)
                if self.include_path(relative_file_path):
                    included_files.append(relative_file_path)

        return included_files

    @cached_property
    def normalized_included_files(self):
        if self._on_windows:
            return [f.replace('\\', '/') for f in self.included_files]

        return self.included_files

    @cached_property
    def artifact_globs(self):
        artifact_globs = []
        separation = self.config_options.get('separate', False) is not False
        compiled_extension = '.pyd' if self._on_windows else '.so'

        for included_file in self.included_files:
            root, _ = os.path.splitext(included_file)
            artifact_globs.append(f'{root}.*{compiled_extension}')

            if separation:
                artifact_globs.append(f'{root}__mypyc.*{compiled_extension}')

        if not separation:
            artifact_globs.append(f'*__mypyc.*{compiled_extension}')

        return artifact_globs

    @cached_property
    def normalized_artifact_globs(self):
        if self._on_windows:
            return [f.replace('\\', '/') for f in self.artifact_globs]

        return self.artifact_globs

    @cached_property
    def artifact_patterns(self):
        # Match the exact path starting at the project root
        return [f'/{artifact_glob}' for artifact_glob in self.normalized_artifact_globs]

    def clean(self, versions):
        from glob import iglob

        for artifact_glob in self.artifact_globs:
            absolute_glob = os.path.join(self.root, artifact_glob)
            for artifact in iglob(absolute_glob):
                os.remove(artifact)

    def initialize(self, version, build_data):
        if self.target_name != 'wheel':
            return

        # Hopefully there will be an API for this soon:
        # https://github.com/python/mypy/blob/v0.930/mypyc/__main__.py
        with TemporaryDirectory() as temp_dir:
            temp_dir = os.path.realpath(temp_dir)

            # Prevent temporary files from being written inside the project by both Mypy and setuptools
            shared_temp_build_dir = os.path.join(temp_dir, 'build')
            temp_build_dir = os.path.join(temp_dir, 'tmp')
            os.mkdir(shared_temp_build_dir)
            os.mkdir(temp_build_dir)

            options = self.config_options.copy()
            options['target_dir'] = shared_temp_build_dir

            setup_file = os.path.join(temp_dir, 'setup.py')
            with open(setup_file, 'w', encoding='utf-8') as f:
                f.write(construct_setup_file(*self.config_mypy_args, *self.normalized_included_files, **options))

            process = subprocess.run(
                [
                    sys.executable,
                    setup_file,
                    'build_ext',
                    '--inplace',
                    '--build-lib',
                    shared_temp_build_dir,
                    '--build-temp',
                    temp_build_dir,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if process.returncode:  # no cov
                raise Exception(f'Error while invoking Mypyc:\n{process.stdout.decode("utf-8")}')

        # Success, now finalize build data
        build_data['infer_tag'] = True
        build_data['zip_safe'] = False
        build_data['artifacts'].extend(self.artifact_patterns)
