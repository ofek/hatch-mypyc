# hatch-mypyc

| | |
| --- | --- |
| CI/CD | [![CI - Test](https://github.com/ofek/hatch-mypyc/actions/workflows/test.yml/badge.svg)](https://github.com/ofek/hatch-mypyc/actions/workflows/test.yml) |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/hatch-mypyc.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/hatch-mypyc/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-mypyc.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/hatch-mypyc/) |
| Meta | [![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/ambv/black) [![imports - isort](https://img.shields.io/badge/imports-isort-ef8336.svg)](https://github.com/pycqa/isort) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) [![GitHub Sponsors](https://img.shields.io/github/sponsors/ofek?logo=GitHub%20Sponsors&style=social)](https://github.com/sponsors/ofek) |

-----

This provides a [build hook](https://ofek.dev/hatch/dev/config/build/#build-hooks) plugin for [Hatch](https://github.com/ofek/hatch) that compiles code with [Mypyc](https://github.com/mypyc/mypyc).

**Table of Contents**

- [Configuration](#configuration)
  - [File selection](#file-selection)
    - [Include](#include)
    - [Exclude](#exclude)
  - [Mypy arguments](#mypy-arguments)
  - [Options](#options)
- [License](#license)

## Configuration

The [build hook plugin](https://ofek.dev/hatch/dev/plugins/build-hook/) name is `mypyc`.

- ***pyproject.toml***

    ```toml
    [tool.hatch.build.targets.wheel.hooks.mypyc]
    dependencies = ["hatch-mypyc"]
    ```

- ***hatch.toml***

    ```toml
    [build.targets.wheel.hooks.mypyc]
    dependencies = ["hatch-mypyc"]
    ```

### File selection

Every entry represents a [Git-style glob pattern](https://git-scm.com/docs/gitignore#_pattern_format).

#### Include

This option is required.

```toml
[build.targets.wheel.hooks.mypyc]
include = ["/pkg"]
```

#### Exclude

```toml
[build.targets.wheel.hooks.mypyc]
exclude = ["__main__.py"]
```

### Mypy arguments

You can specify extra [Mypy arguments](https://mypy.readthedocs.io/en/stable/command_line.html) with the `mypy-args` option.

```toml
[build.targets.wheel.hooks.mypyc]
mypy-args = [
  "--disallow-untyped-defs",
]
```

### Options

You can specify `options` that affect the behavior of [mypycify](https://github.com/python/mypy/blob/v0.930/mypyc/build.py#L429).

```toml
[build.targets.wheel.hooks.mypyc.options]
opt_level = "3"
```

## License

`hatch-mypyc` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
