# hatch-mypyc

| | |
| --- | --- |
| CI/CD | [![CI - Test](https://github.com/ofek/hatch-mypyc/actions/workflows/test.yml/badge.svg)](https://github.com/ofek/hatch-mypyc/actions/workflows/test.yml) [![CD - Build](https://github.com/ofek/hatch-mypyc/actions/workflows/build.yml/badge.svg)](https://github.com/ofek/hatch-mypyc/actions/workflows/build.yml) |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/hatch-mypyc.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/hatch-mypyc/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-mypyc.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/hatch-mypyc/) |
| Meta | [![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/ambv/black) [![imports - isort](https://img.shields.io/badge/imports-isort-ef8336.svg)](https://github.com/pycqa/isort) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) [![GitHub Sponsors](https://img.shields.io/github/sponsors/ofek?logo=GitHub%20Sponsors&style=social)](https://github.com/sponsors/ofek) |

-----

This provides a [build hook](https://ofek.dev/hatch/latest/config/build/#build-hooks) plugin for [Hatch](https://github.com/ofek/hatch) that compiles code with [Mypyc](https://github.com/mypyc/mypyc).

**Table of Contents**

- [Configuration](#configuration)
  - [File selection](#file-selection)
  - [Mypy arguments](#mypy-arguments)
  - [Options](#options)
- [Missing types](#missing-types)
- [License](#license)

## Configuration

The [build hook plugin](https://ofek.dev/hatch/latest/plugins/build-hook/) name is `mypyc`.

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

By default, the [standard file selection options](https://ofek.dev/hatch/latest/config/build/#file-selection) will be used. You can override this behavior with the `include`/`exclude` options.

```toml
[build.targets.wheel.hooks.mypyc]
include = ["/pkg"]
exclude = ["__main__.py"]
```

At least one inclusion pattern must be provided overall.

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

Note:

- if `separate` is set to `false` (the default), then you'll need to either set [dev-mode-dirs](https://ofek.dev/hatch/latest/config/build/#dev-mode) for builds or disable [dev-mode](https://ofek.dev/hatch/latest/config/environment/#dev-mode) for environments
- the `target_dir` option is used internally and therefore has no effect

## Missing types

If you need more packages at build time in order to successfully type check, you can use the following options where you [configured the plugin](#configuration):

- `dependencies` - add more dependencies alongside `hatch-mypyc`
- `require-runtime-dependencies` - set to `true` to include dependencies defined in the `project.dependencies` array

## License

`hatch-mypyc` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
