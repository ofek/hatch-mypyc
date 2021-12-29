# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import os
import platform
from glob import glob

import pytest

from .utils import build_project

pytestmark = [pytest.mark.usefixtures('new_project')]


def test():
    compiled_extension = '.pyd' if platform.system() == 'Windows' else '.so'
    shared_lib_pattern = f'*__mypyc.*{compiled_extension}'
    lib_pattern = f'my_app{os.path.sep}*.*{compiled_extension}'

    assert not glob(shared_lib_pattern)
    assert not glob(lib_pattern)

    build_project()

    assert len(glob(shared_lib_pattern)) == 1
    assert len(glob(lib_pattern)) == 2

    build_project('--clean-only')

    assert not glob(shared_lib_pattern)
    assert not glob(lib_pattern)
