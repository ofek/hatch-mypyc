# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    with TemporaryDirectory() as d:
        yield Path(os.path.realpath(d))


@pytest.fixture
def new_project(temp_dir):
    project_dir = temp_dir / 'my-app'
    project_dir.mkdir()

    gitignore_file = project_dir / '.gitignore'
    gitignore_file.write_text('*.so\n*.pyd', encoding='utf-8')

    project_file = project_dir / 'pyproject.toml'
    project_file.write_text(
        """\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-app"
dynamic = ["version"]

[tool.hatch.version]
path = "my_app/__init__.py"

[tool.hatch.build]
packages = ["my_app"]

[tool.hatch.build.targets.wheel.hooks.mypyc]
dependencies = ["hatch-mypyc"]
include = ["/my_app"]
""",
        encoding='utf-8',
    )

    package_dir = project_dir / 'my_app'
    package_dir.mkdir()

    package_root = package_dir / '__init__.py'
    package_root.write_text('__version__ = "1.2.3"', encoding='utf-8')

    fibonacci_file = package_dir / 'fib.py'
    fibonacci_file.write_text(
        """\
def fib(n: int) -> int:
    if n <= 1:
        return n
    else:
        return fib(n - 2) + fib(n - 1)
""",
        encoding='utf-8',
    )

    package_data_file = package_dir / 'driver.yaml'
    package_data_file.write_text('apiVersion: storage.k8s.io/v1', encoding='utf-8')

    origin = os.getcwd()
    os.chdir(project_dir)
    try:
        yield project_dir
    finally:
        os.chdir(origin)
