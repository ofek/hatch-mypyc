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
