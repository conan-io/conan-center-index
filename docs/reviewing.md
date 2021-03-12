# Reviewing policies

The following policies are preferred during the review, but not mandatory:

<!-- toc -->
## Contents

  * [Trailing white-spaces](#trailing-white-spaces)
  * [Quotes](#quotes)
  * [Subfolder Properties](#subfolder-properties)
  * [Order of methods and attributes](#order-of-methods-and-attributes)
  * [License Attribute](#license-attribute)
  * [Test Package](#test-package)
    * [Minimalistic Source Code](#minimalistic-source-code)
    * [Verifying Components](#verifying-components)<!-- endToc -->

## Trailing white-spaces

Avoid trailing white-space characters, if possible

## Quotes

If possible, try to avoid mixing single quotes (`'`) and double quotes (`"`) in python code (`conanfile.py`, `test_package/conanfile.py`). Consistency is preferred.

## Subfolder Properties 

When extracting sources or performing out-of-source builds, it is preferable to use property attributes for these variables.

```py
@property
def _source_subfolder(self):
    return "source_subfolder"

@property
def _build_subfolder(self):
    return "build_subfolder"
```

## Order of methods and attributes

Prefer the following order of documented methods in python code (`conanfile.py`, `test_package/conanfile.py`):

- init
- set_name
- set_version
- export
- export_sources
- config_options
- configure
- requirements
- package_id
- build_id
- build_requirements
- system_requirements
- source
- imports
- build
- package
- package_info
- deploy
- test

the order above resembles the execution order of methods on CI. therefore, for instance, `build` is always executed before `package` method, so `build` should appear before the
`package` in `conanfile.py`.

## License Attribute

The mandatory license attribute of each recipe **should** be a [SPDX license](https://spdx.org/licenses/) [short Identifiers](https://spdx.dev/ids/) when applicable.

## Test Package

### Minimalistic Source Code

The contents of `test_package.c` or `test_package.cpp` should be as minimal as possible, including a few headers at most with simple instatiation of objects to ensure linkage
and dependencies are correct.

### Verifying Components

When components are defined in the `package_info` in `conanfile.py` the following conditions are desired

- use the `cmake_find_package` or `cmake_find_package_multi` generators in `test_package/conanfile.py`
- corresponding call to `find_package()` with the components _explicitly_ used in `target_link_libraries`
