# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import os
import platform
import subprocess
import sys
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

    process = subprocess.run(
        [sys.executable, '-m', 'hatchling', 'build', '-t', 'wheel', '--clean-only'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if process.returncode:  # no cov
        raise Exception(process.stdout.decode('utf-8'))

    assert not glob(shared_lib_pattern)
    assert not glob(lib_pattern)
