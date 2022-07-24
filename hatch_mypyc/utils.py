# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import os


def construct_setup_file(package_source, *args, **kwargs):
    # Ensure that setuptools is imported first
    contents = """\
from setuptools import setup
from mypyc.build import mypycify

setup(
    name='mypyc_output',
    ext_modules=mypycify(
        [{}
        ],{}
    ),{}
)
"""

    package_dir_data = ''
    if package_source:
        package_source = package_source.replace(os.path.sep, '/')
        package_dir_data = f"\n    package_dir={{'': '{package_source}'}},"

    return contents.format(
        ''.join(f'\n            {arg!r},' for arg in args),
        ''.join(f'\n        {key}={value!r},' for key, value in kwargs.items()),
        package_dir_data,
    )


def installed_in_prefix() -> bool:  # no cov
    # pip always sets this
    python_path = os.environ.get('PYTHONPATH', '')
    if not python_path:
        return False

    paths = python_path.split(os.pathsep)

    # pip only sets one location, see:
    # https://github.com/pypa/pip/blob/21.3.1/src/pip/_internal/build_env.py#L137
    if len(paths) > 1:
        return False

    temp_build_dir = os.path.dirname(paths[0])

    # https://github.com/pypa/pip/blob/21.3.1/src/pip/_internal/build_env.py#L74
    # https://github.com/pypa/pip/blob/21.3.1/src/pip/_internal/utils/temp_dir.py#L164
    if not os.path.basename(temp_build_dir).startswith('pip-build-env-'):
        return False

    wheel_requirements_install_path = os.path.join(temp_build_dir, 'normal', 'lib', 'site-packages')
    if not os.path.isdir(wheel_requirements_install_path):
        return False

    return True
