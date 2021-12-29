# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import subprocess
import sys


def build_project(*args):
    process = subprocess.run(
        [sys.executable, '-m', 'hatchling', 'build', *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    if process.returncode:  # no cov
        raise Exception(process.stdout.decode('utf-8'))
