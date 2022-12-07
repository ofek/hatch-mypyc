# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import os
import platform
import subprocess
import sys
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import pathspec
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from hatch_mypyc.utils import construct_setup_file, installed_in_prefix


class MypycBuildHook(BuildHookInterface):
    PLUGIN_NAME = 'mypyc'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__config_mypy_args = None
        self.__config_options = None
        self.__config_separation = None
        self.__config_build_dir = None
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
        self.__compiled_extension = '.pyd' if self._on_windows else '.so'

    @property
    def compiled_extension(self):
        return self.__compiled_extension

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
    def config_separation(self):
        if self.__config_separation is None:
            self.__config_separation = self.config_options.get('separate', False) is not False

        return self.__config_separation

    @property
    def config_build_dir(self):
        if self.__config_build_dir is None:
            build_dir = os.environ.get('HATCH_MYPYC_BUILD_DIR', self.config_options.get('build-dir', ''))
            if build_dir and not os.path.isabs(build_dir):
                build_dir = os.path.join(self.root, build_dir)

            self.__config_build_dir = build_dir

        return self.__config_build_dir

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
        if self.__config_include is None and self.config_include:
            self.__include_spec = pathspec.PathSpec.from_lines(
                pathspec.patterns.GitWildMatchPattern, self.config_include
            )

        return self.__include_spec

    @property
    def exclude_spec(self):
        if self.__exclude_spec is None and self.config_exclude:
            self.__exclude_spec = pathspec.PathSpec.from_lines(
                pathspec.patterns.GitWildMatchPattern, self.config_exclude
            )

        return self.__exclude_spec

    def include_path(self, relative_path):
        return self.path_is_included(relative_path) and not self.path_is_excluded(relative_path)

    def path_is_included(self, relative_path):
        if self.include_spec is None:  # no cov
            return True

        return self.include_spec.match_file(relative_path)

    def path_is_excluded(self, relative_path):
        if self.exclude_spec is None:  # no cov
            return False

        return self.exclude_spec.match_file(relative_path)

    @property
    def included_files(self):
        if self.__included_files is None:
            included_files = []

            for included_file in self.build_config.builder.recurse_included_files():
                relative_path = included_file.relative_path
                if relative_path.endswith('.py') and self.include_path(relative_path):
                    included_files.append(relative_path)

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

            # TODO: investigate using more specific patterns to avoid having to clean everything before each run
            for included_file in self.included_files:
                root, _ = os.path.splitext(included_file)
                artifact_globs.append(f'{root}.*{self.compiled_extension}')

                if self.config_separation:
                    artifact_globs.append(f'{root}__mypyc.*{self.compiled_extension}')

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

    def get_forced_inclusion_map(self):
        inclusion_map = {}
        if not self.config_separation:
            from glob import iglob

            pattern = f'*__mypyc.*{self.compiled_extension}'
            if self.package_source:
                pattern = os.path.join(self.package_source, pattern)

            for path in iglob(os.path.join(self.root, pattern)):
                inclusion_map[path] = os.path.relpath(path, self.root)

        return inclusion_map

    def clean(self, versions):
        from glob import iglob

        for path in self.get_forced_inclusion_map():
            os.remove(path)

        for artifact_glob in self.artifact_globs:
            absolute_glob = os.path.join(self.root, artifact_glob)
            for artifact in iglob(absolute_glob):
                os.remove(artifact)

    @contextmanager
    def hide_project_file(self):
        # TODO: remove this and bump setuptools when it supports PEP 639
        project_file = os.path.join(self.root, 'pyproject.toml')
        project_file_backup = os.path.join(self.root, 'pyproject.toml.bak')

        os.replace(project_file, project_file_backup)
        try:
            yield
        finally:
            os.replace(project_file_backup, project_file)

    @contextmanager
    def get_build_dirs(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir = os.path.realpath(temp_dir)
            if self.config_build_dir:
                yield self.config_build_dir, temp_dir
            # Prevent temporary files from being written inside the project by both Mypy and setuptools
            else:
                yield temp_dir, temp_dir

    def initialize(self, version, build_data):
        if self.target_name != 'wheel':
            return

        # Hopefully there will be an API for this soon:
        # https://github.com/python/mypy/blob/v0.961/mypyc/__main__.py
        with self.get_build_dirs() as (intermediate_build_dir, temp_dir):
            shared_temp_build_dir = os.path.join(intermediate_build_dir, 'build')
            temp_build_dir = os.path.join(intermediate_build_dir, 'tmp')
            os.mkdir(shared_temp_build_dir)
            os.mkdir(temp_build_dir)

            options = self.config_options.copy()
            options['target_dir'] = shared_temp_build_dir

            mypy_args = list(self.config_mypy_args)
            # Prevent horribly breaking users' global environments
            if installed_in_prefix() and '--install-types' in mypy_args:  # no cov
                mypy_args.remove('--install-types')

            setup_file = os.path.join(temp_dir, 'setup.py')
            with open(setup_file, 'w', encoding='utf-8') as f:
                f.write(
                    construct_setup_file(self.package_source, *mypy_args, *self.normalized_included_files, **options)
                )

            # We don't know the exact naming scheme of the files produced using this interpreter,
            # so always clean to prevent including files from other runs
            self.clean([version])

            with self.hide_project_file():
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
        build_data['force_include'].update(self.get_forced_inclusion_map())
