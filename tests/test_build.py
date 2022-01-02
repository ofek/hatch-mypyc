# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import zipfile

from packaging.tags import sys_tags

from .utils import build_project


def test_no_exclusion(new_project, compiled_extension):
    build_project()

    build_dir = new_project / 'dist'
    assert build_dir.is_dir()

    artifacts = list(build_dir.iterdir())
    assert len(artifacts) == 1
    wheel_file = artifacts[0]

    best_matching_tag = next(sys_tags())
    assert wheel_file.name == f'my_app-1.2.3-{best_matching_tag}.whl'

    extraction_directory = new_project.parent / '_archive'
    extraction_directory.mkdir()

    with zipfile.ZipFile(str(wheel_file), 'r') as zip_archive:
        zip_archive.extractall(str(extraction_directory))

    root_paths = list(extraction_directory.iterdir())
    assert len(root_paths) == 3
    assert len([root_path for root_path in root_paths if root_path.name.startswith('my_app')]) == 2
    assert len([root_path for root_path in root_paths if root_path.name.endswith(compiled_extension)]) == 1

    metadata_directory = extraction_directory / 'my_app-1.2.3.dist-info'
    assert metadata_directory.is_dir()

    wheel_metadata_file = metadata_directory / 'WHEEL'
    assert wheel_metadata_file.is_file()
    assert 'Root-Is-Purelib: false' in wheel_metadata_file.read_text(encoding='utf-8')

    extracted_package_dir = extraction_directory / 'my_app'
    assert extracted_package_dir.is_dir()

    distributed_files = list(extracted_package_dir.iterdir())
    assert len(distributed_files) == 5

    root_files = 0
    fibonacci_files = 0
    for distributed_file in distributed_files:
        if distributed_file.name.startswith('__init__'):
            root_files += 1
        elif distributed_file.name.startswith('fib'):
            fibonacci_files += 1

    assert root_files == 2
    assert fibonacci_files == 2


def test_exclusion(new_project, compiled_extension):
    project_file = new_project / 'pyproject.toml'
    contents = project_file.read_text(encoding='utf-8')
    contents += '\nexclude = ["__main__.py"]'
    project_file.write_text(contents, encoding='utf-8')

    package_main = new_project / 'my_app' / '__main__.py'
    package_main.write_text(
        """\
if __name__ == '__main__':
    from .fib import fib
    print(fib())
""",
        encoding='utf-8',
    )

    build_project()

    build_dir = new_project / 'dist'
    assert build_dir.is_dir()

    artifacts = list(build_dir.iterdir())
    assert len(artifacts) == 1
    wheel_file = artifacts[0]

    best_matching_tag = next(sys_tags())
    assert wheel_file.name == f'my_app-1.2.3-{best_matching_tag}.whl'

    extraction_directory = new_project.parent / '_archive'
    extraction_directory.mkdir()

    with zipfile.ZipFile(str(wheel_file), 'r') as zip_archive:
        zip_archive.extractall(str(extraction_directory))

    root_paths = list(extraction_directory.iterdir())
    assert len(root_paths) == 3
    assert len([root_path for root_path in root_paths if root_path.name.startswith('my_app')]) == 2
    assert len([root_path for root_path in root_paths if root_path.name.endswith(compiled_extension)]) == 1

    metadata_directory = extraction_directory / 'my_app-1.2.3.dist-info'
    assert metadata_directory.is_dir()

    wheel_metadata_file = metadata_directory / 'WHEEL'
    assert wheel_metadata_file.is_file()
    assert 'Root-Is-Purelib: false' in wheel_metadata_file.read_text(encoding='utf-8')

    extracted_package_dir = extraction_directory / 'my_app'
    assert extracted_package_dir.is_dir()

    distributed_files = list(extracted_package_dir.iterdir())
    assert len(distributed_files) == 6

    root_files = 0
    fibonacci_files = 0
    for distributed_file in distributed_files:
        if distributed_file.name.startswith('__init__'):
            root_files += 1
        elif distributed_file.name.startswith('fib'):
            fibonacci_files += 1

    assert root_files == 2
    assert fibonacci_files == 2


def test_separation(new_project):
    project_file = new_project / 'pyproject.toml'
    contents = project_file.read_text(encoding='utf-8')
    contents += '\noptions = { separate = true }'
    project_file.write_text(contents, encoding='utf-8')

    build_project()

    build_dir = new_project / 'dist'
    assert build_dir.is_dir()

    artifacts = list(build_dir.iterdir())
    assert len(artifacts) == 1
    wheel_file = artifacts[0]

    best_matching_tag = next(sys_tags())
    assert wheel_file.name == f'my_app-1.2.3-{best_matching_tag}.whl'

    extraction_directory = new_project.parent / '_archive'
    extraction_directory.mkdir()

    with zipfile.ZipFile(str(wheel_file), 'r') as zip_archive:
        zip_archive.extractall(str(extraction_directory))

    root_paths = list(extraction_directory.iterdir())
    assert len(root_paths) == 2
    assert len([root_path for root_path in root_paths if root_path.name.startswith('my_app')]) == 2

    metadata_directory = extraction_directory / 'my_app-1.2.3.dist-info'
    assert metadata_directory.is_dir()

    wheel_metadata_file = metadata_directory / 'WHEEL'
    assert wheel_metadata_file.is_file()
    assert 'Root-Is-Purelib: false' in wheel_metadata_file.read_text(encoding='utf-8')

    extracted_package_dir = extraction_directory / 'my_app'
    assert extracted_package_dir.is_dir()

    distributed_files = list(extracted_package_dir.iterdir())
    assert len(distributed_files) == 5

    root_files = 0
    fibonacci_files = 0
    for distributed_file in distributed_files:
        if distributed_file.name.startswith('__init__'):
            root_files += 1
        elif distributed_file.name.startswith('fib'):
            fibonacci_files += 1

    assert root_files == 1
    assert fibonacci_files == 3


def test_src_layout(new_project, compiled_extension):
    project_file = new_project / 'pyproject.toml'
    contents = project_file.read_text(encoding='utf-8')
    contents = contents.replace('my_app', 'src/my_app')
    project_file.write_text(contents, encoding='utf-8')
    package_dir = new_project / 'my_app'
    src_dir = new_project / 'src'
    src_dir.mkdir()
    package_dir.replace(src_dir / 'my_app')

    build_project()

    build_dir = new_project / 'dist'
    assert build_dir.is_dir()

    artifacts = list(build_dir.iterdir())
    assert len(artifacts) == 1
    wheel_file = artifacts[0]

    best_matching_tag = next(sys_tags())
    assert wheel_file.name == f'my_app-1.2.3-{best_matching_tag}.whl'

    extraction_directory = new_project.parent / '_archive'
    extraction_directory.mkdir()

    with zipfile.ZipFile(str(wheel_file), 'r') as zip_archive:
        zip_archive.extractall(str(extraction_directory))

    root_paths = list(extraction_directory.iterdir())
    assert len(root_paths) == 3
    assert len([root_path for root_path in root_paths if root_path.name.startswith('my_app')]) == 2
    assert len([root_path for root_path in root_paths if root_path.name.endswith(compiled_extension)]) == 1

    metadata_directory = extraction_directory / 'my_app-1.2.3.dist-info'
    assert metadata_directory.is_dir()

    wheel_metadata_file = metadata_directory / 'WHEEL'
    assert wheel_metadata_file.is_file()
    assert 'Root-Is-Purelib: false' in wheel_metadata_file.read_text(encoding='utf-8')

    extracted_package_dir = extraction_directory / 'my_app'
    assert extracted_package_dir.is_dir()

    distributed_files = list(extracted_package_dir.iterdir())
    assert len(distributed_files) == 5

    root_files = 0
    fibonacci_files = 0
    for distributed_file in distributed_files:
        if distributed_file.name.startswith('__init__'):
            root_files += 1
        elif distributed_file.name.startswith('fib'):
            fibonacci_files += 1

    assert root_files == 2
    assert fibonacci_files == 2


def test_target_not_wheel(new_project):
    project_file = new_project / 'pyproject.toml'
    contents = project_file.read_text(encoding='utf-8')
    contents = contents.replace('[tool.hatch.build.targets.wheel.hooks.mypyc]', '[tool.hatch.build.hooks.mypyc]')
    project_file.write_text(contents, encoding='utf-8')

    build_project('-t', 'sdist')

    build_dir = new_project / 'dist'
    assert build_dir.is_dir()

    artifacts = list(build_dir.iterdir())
    assert len(artifacts) == 1

    assert artifacts[0].name.endswith('.tar.gz')
