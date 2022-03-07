# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import os
import platform
import subprocess
import sys
from tempfile import TemporaryDirectory

import pathspec
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from .utils import construct_setup_file, patch_mypy_prefix_module_discovery


class MypycBuildHook(BuildHookInterface):
    PLUGIN_NAME = 'mypyc'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__config_mypy_args = None
        self.__config_options = None
        self.__config_include = None
        self.__config_exclude = None
        self.__package_source = None
        self.__include_spec = None
        self.__exclude_spec = None
        self.__included_files = None
        self.__normalized_included_files = None
        self.__artifact_globs = None
        self.__normalized_artifact_globs = None
        self.__artifact_patterns = None

        self._on_windows = platform.system() == 'Windows'

    @property
    def config_mypy_args(self):
        if self.__config_mypy_args is None:
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

            self.__config_mypy_args = mypy_args

        return self.__config_mypy_args

    @property
    def config_options(self):
        if self.__config_options is None:
            options = self.config.get('options', {})
            if not isinstance(options, dict):
                raise TypeError(f'Option `options` for build hook `{self.PLUGIN_NAME}` must be a table')

            self.__config_options = options

        return self.__config_options

    @property
    def config_include(self):
        if self.__config_include is None:
            patterns = self.config.get('include', [])
            if isinstance(patterns, list):
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

            self.__config_include = patterns

        return self.__config_include

    @property
    def config_exclude(self):
        if self.__config_exclude is None:
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

            self.__config_exclude = patterns

        return self.__config_exclude

    @property
    def package_source(self):
        if self.__package_source is None:
            if self.build_config.sources:
                # Just support one source for now
                self.__package_source = list(self.build_config.sources)[0][:-1]
            else:
                self.__package_source = ''

        return self.__package_source

    @property
    def include_spec(self):
        if self.__include_spec is None:
            if self.config_include:
                self.__include_spec = pathspec.PathSpec.from_lines(
                    pathspec.patterns.GitWildMatchPattern, self.config_include
                )
            elif self.build_config.include_spec is not None:
                self.__include_spec = self.build_config.include_spec
            else:
                raise ValueError(f'Option `include` for build hook `{self.PLUGIN_NAME}` is required')

        return self.__include_spec

    @property
    def exclude_spec(self):
        if self.__exclude_spec is None:
            if self.config_exclude:
                self.__exclude_spec = pathspec.PathSpec.from_lines(
                    pathspec.patterns.GitWildMatchPattern, self.config_exclude
                )
            else:
                self.__exclude_spec = self.build_config.exclude_spec

        return self.__exclude_spec

    def include_path(self, relative_path):
        return self.include_spec.match_file(relative_path) and not self.path_is_excluded(relative_path)

    def path_is_excluded(self, relative_path):
        if self.exclude_spec is None:  # no cov
            return False

        return self.exclude_spec.match_file(relative_path)

    @property
    def included_files(self):
        if self.__included_files is None:
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

            self.__included_files = included_files

        return self.__included_files

    @property
    def normalized_included_files(self):
        if self.__normalized_included_files is None:
            if self._on_windows:
                self.__normalized_included_files = [f.replace('\\', '/') for f in self.included_files]
            else:
                self.__normalized_included_files = self.included_files

        return self.__normalized_included_files

    @property
    def artifact_globs(self):
        if self.__artifact_globs is None:
            artifact_globs = []
            separation = self.config_options.get('separate', False) is not False
            compiled_extension = '.pyd' if self._on_windows else '.so'

            # TODO: investigate using more specific patterns to avoid having to clean everything before each run
            for included_file in self.included_files:
                root, _ = os.path.splitext(included_file)
                artifact_globs.append(f'{root}.*{compiled_extension}')

                if separation:
                    artifact_globs.append(f'{root}__mypyc.*{compiled_extension}')

            if not separation:
                if self.package_source:
                    artifact_globs.append(f'{self.package_source}{os.path.sep}*__mypyc.*{compiled_extension}')
                else:
                    artifact_globs.append(f'*__mypyc.*{compiled_extension}')

            self.__artifact_globs = artifact_globs

        return self.__artifact_globs

    @property
    def normalized_artifact_globs(self):
        if self.__normalized_artifact_globs is None:
            if self._on_windows:
                self.__normalized_artifact_globs = [f.replace('\\', '/') for f in self.artifact_globs]
            else:
                self.__normalized_artifact_globs = self.artifact_globs

        return self.__normalized_artifact_globs

    @property
    def artifact_patterns(self):
        if self.__artifact_patterns is None:
            # Match the exact path starting at the project root
            self.__artifact_patterns = [f'/{artifact_glob}' for artifact_glob in self.normalized_artifact_globs]

        return self.__artifact_patterns

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

            # Only applies when building with pip
            mypy_installed_in_prefix = patch_mypy_prefix_module_discovery()

            mypy_args = list(self.config_mypy_args)
            # Prevent horribly breaking users' global environments
            if mypy_installed_in_prefix and '--install-types' in mypy_args:
                mypy_args.remove('--install-types')

            setup_file = os.path.join(temp_dir, 'setup.py')
            with open(setup_file, 'w', encoding='utf-8') as f:
                f.write(
                    construct_setup_file(self.package_source, *mypy_args, *self.normalized_included_files, **options)
                )

            # We don't know the exact naming scheme of the files produced using this interpreter,
            # so always clean to prevent including files from other runs
            self.clean([version])

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
        build_data['pure_python'] = False
        build_data['artifacts'].extend(self.artifact_patterns)
