# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
from hatch_mypyc.utils import construct_setup_file


class TestConstructSetupFile:
    def test_no_arguments(self):
        assert (
            construct_setup_file([], opt_level='3')
            == """\
from setuptools import setup
from mypyc.build import mypycify

setup(
    name='mypyc_output',
    ext_modules=mypycify(
        [
        ],
        opt_level='3',
    ),
)
"""
        )

    def test_one_argument(self):
        assert (
            construct_setup_file([], 'foo', opt_level='3')
            == """\
from setuptools import setup
from mypyc.build import mypycify

setup(
    name='mypyc_output',
    ext_modules=mypycify(
        [
            'foo',
        ],
        opt_level='3',
    ),
)
"""
        )

    def test_multiple_arguments(self):
        assert (
            construct_setup_file([], 'foo', 'bar', opt_level='3')
            == """\
from setuptools import setup
from mypyc.build import mypycify

setup(
    name='mypyc_output',
    ext_modules=mypycify(
        [
            'foo',
            'bar',
        ],
        opt_level='3',
    ),
)
"""
        )

    def test_no_options(self):
        assert (
            construct_setup_file([], 'foo', 'bar')
            == """\
from setuptools import setup
from mypyc.build import mypycify

setup(
    name='mypyc_output',
    ext_modules=mypycify(
        [
            'foo',
            'bar',
        ],
    ),
)
"""
        )

    def test_packages_root(self):
        assert (
            construct_setup_file('', 'foo')
            == """\
from setuptools import setup
from mypyc.build import mypycify

setup(
    name='mypyc_output',
    ext_modules=mypycify(
        [
            'foo',
        ],
    ),
)
"""
        )

    def test_packages_source(self):
        assert (
            construct_setup_file('src', 'foo')
            == """\
from setuptools import setup
from mypyc.build import mypycify

setup(
    name='mypyc_output',
    ext_modules=mypycify(
        [
            'foo',
        ],
    ),
    package_dir={'': 'src'},
)
"""
        )
