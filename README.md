# hatch-mypyc

| | |
| --- | --- |
| CI/CD | [![CI - Test](https://github.com/ofek/hatch-mypyc/actions/workflows/test.yml/badge.svg)](https://github.com/ofek/hatch-mypyc/actions/workflows/test.yml) [![CD - Build](https://github.com/ofek/hatch-mypyc/actions/workflows/build.yml/badge.svg)](https://github.com/ofek/hatch-mypyc/actions/workflows/build.yml) |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/hatch-mypyc.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/hatch-mypyc/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-mypyc.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/hatch-mypyc/) |
| Meta | [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/ambv/black) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) [![GitHub Sponsors](https://img.shields.io/github/sponsors/ofek?logo=GitHub%20Sponsors&style=social)](https://github.com/sponsors/ofek) |

-----

This provides a [build hook](https://hatch.pypa.io/latest/config/build/#build-hooks) plugin for [Hatch](https://github.com/pypa/hatch) that compiles code with [Mypyc](https://github.com/mypyc/mypyc).

**Table of Contents**

- [Configuration](#configuration)
  - [File selection](#file-selection)
  - [Mypy arguments](#mypy-arguments)
  - [Options](#options)
- [Missing types](#missing-types)
- [License](#license)

## Configuration

The [build hook plugin](https://hatch.pypa.io/latest/plugins/build-hook/) name is `mypyc`.

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

By default, all files included using the [standard file selection options](https://hatch.pypa.io/latest/config/build/#file-selection) with a `.py` extension will be targeted. You can narrow what files to compile to an even smaller subset with the `include`/`exclude` options, which represent [Git-style glob patterns](https://git-scm.com/docs/gitignore#_pattern_format).

```toml
[build.targets.wheel.hooks.mypyc]
include = ["/src/pkg/server"]
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

Note:

- the `target_dir` option is used internally and therefore has no effect

## Missing types

If you need more packages at build time in order to successfully type check, you can use the following options where you [configured the plugin](#configuration):

- `dependencies` - add more dependencies alongside `hatch-mypyc`
- `require-runtime-dependencies` - set to `true` to include dependencies defined in the `project.dependencies` array
- `require-runtime-features` - set to an array of named dependency groups that are defined in `project.optional-dependencies`

## License

`hatch-mypyc` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
