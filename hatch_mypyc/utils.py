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


def patch_mypy_prefix_module_discovery() -> bool:  # no cov
    """
    pip does not use a virtual environment for builds so we need to patch
    Mypy in order for it to recognize installed build requirements
    """
    # pip always sets this, but we cannot merely set MYPYPATH with it b/c we encounter:
    # https://github.com/python/mypy/issues/10829
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

    # At this point, assume we are indeed being built by pip and error out if patching fails
    #
    # https://github.com/python/mypy/issues/5701#issuecomment-751494692
    patch_file = os.path.join(wheel_requirements_install_path, 'mypy', 'pyinfo.py')
    if not os.path.isfile(patch_file):
        raise OSError('Cannot find Mypy file to patch')

    with open(patch_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for _patch_start_index, line in enumerate(lines, 1):
        if line.startswith('def getsitepackages():'):
            break
    else:
        raise ValueError('Cannot apply patch to Mypy file')

    for line in [
        '    # type: () -> List[str]',
        '    return sys.path',
        '',
        '',
        'def _get_site_packages():',
    ][::-1]:
        lines.insert(_patch_start_index, f'{line}\n')

    with open(patch_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return True
