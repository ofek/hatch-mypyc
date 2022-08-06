# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import os
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

import pytest


@pytest.fixture(scope='session')
def compiled_extension() -> str:
    return '.pyd' if sys.platform == 'win32' else '.so'


@pytest.fixture(scope='session')
def plugin_dir() -> Generator[Path, None, None]:
    with TemporaryDirectory() as d:
        directory = Path(d, 'plugin')
        shutil.copytree(Path.cwd(), directory, ignore=shutil.ignore_patterns('.git'))

        yield directory.resolve()


@pytest.fixture
def new_project(plugin_dir, compiled_extension, tmp_path) -> Generator[Path, None, None]:
    project_dir = tmp_path / 'my-app'
    project_dir.mkdir()

    gitignore_file = project_dir / '.gitignore'
    gitignore_file.write_text(f'*{compiled_extension}', encoding='utf-8')

    project_file = project_dir / 'pyproject.toml'
    project_file.write_text(
        f"""\
[build-system]
requires = ["hatchling", "hatch-mypyc @ {plugin_dir.as_uri()}"]
build-backend = "hatchling.build"

[project]
name = "my-app"
dependencies = []
dynamic = ["version"]

[tool.hatch.version]
path = "my_app/__init__.py"

[tool.hatch.build.targets.wheel.hooks.mypyc]
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
