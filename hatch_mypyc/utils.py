# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT


def construct_setup_file(*args, **kwargs):
    # Ensure that setuptools is imported first
    contents = """\
from setuptools import setup
from mypyc.build import mypycify

setup(
    name='mypyc_output',
    ext_modules=mypycify(
        [{}
        ],{}
    ),
)
"""

    return contents.format(
        ''.join(f'\n            {arg!r},' for arg in args),
        ''.join(f'\n        {key}={value!r},' for key, value in kwargs.items()),
    )
