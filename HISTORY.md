# History

-----

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## 0.14.1 - 2022-12-29

***Fixed:***

- Prevent the installation of a version of packaging that is known to be broken on macOS

## 0.14.0 - 2022-08-28

***Added:***

- Add `build-dir` option to persist intermediate artifacts

## 0.13.0 - 2022-08-14

***Changed:***

- The `include`/`exclude` options are now applied after the standard file selection options rather than used as overrides

***Added:***

- Bump the minimum supported version of Hatchling

## 0.12.0 - 2022-07-24

***Added:***

- Bump the minimum supported version of Mypy in order to remove the patch when building with `pip` now that it properly searches `sys.path` for PEP 561 compliant packages
- Officially support Python 3.11
- Bump the minimum supported version of Hatchling

## 0.11.1 - 2022-07-03

***Fixed:***

- Don't rely on the current working directory being the project root
- Relax setuptools pin

## 0.11.0 - 2022-07-03

***Added:***

- Bump the minimum supported version of Hatchling

## 0.10.0 - 2022-06-13

***Added:***

- Bump the minimum supported version of dependencies

***Fixed:***

- Properly work around setuptools' lack of support for PEP 639

## 0.9.1 - 2022-03-25

***Fixed:***

- Cap the version of setuptools until it supports PEP 639

## 0.9.0 - 2022-03-07

***Added:***

- Bump the minimum supported version of Hatchling

## 0.8.0 - 2022-02-27

***Added:***

- Support newer versions of Hatchling

## 0.7.0 - 2022-02-13

***Added:***

- Bump the minimum supported version of Hatchling

## 0.6.0 - 2022-01-19

***Added:***

- Bump the minimum supported version of Hatchling

***Fixed:***

- Properly ignore artifacts from other runs

## 0.5.0 - 2022-01-12

***Added:***

- Bump the minimum supported version of Hatchling, Mypy, and setuptools

***Fixed:***

- Patch Mypy when building with `pip` to fix access to build requirements

## 0.4 - 2022-01-04

***Added:***

- Support Python 3.7

## 0.3 - 2022-01-02

***Added:***

- Bump the minimum supported version of Hatchling for a fix for projects with a `src`-layout structure

## 0.2 - 2021-12-31

***Added:***

- Default to using the standard file selection options for easier configuration
- Support `src`-layout project structures

## 0.1 - 2021-12-29

This is the initial public release.
