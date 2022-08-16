# Supported platforms and configurations

<!-- toc -->
## Contents

  * [Introduction](#introduction)
    * [Build Images](#build-images)
  * [Windows](#windows)
  * [Linux](#linux)
  * [MacOS](#macos)<!-- endToc -->

## Introduction

The pipeline iterates a fixed list of profiles for every Conan reference,
it computes the packageID for each profile and discard duplicates. Then it
builds the packages for the remaining profiles and upload them to
[JFrog ConanCenter](https://conan.io/center/) once the pull-request is merged.

Because duplicated packageIDs are discarded, the pipeline iterates the
profiles always in the same order and the profiles selected to build when
there is a duplicate follow some rules:

 * Static linkage (option `shared=False`) is preferred over dynamic linking.
 * On Windows, `MT/MTd` runtime linkage goes before `MD/MDd` linkage.
 * Optimized binaries (`build_type=Release`) are preferred over its _debug_ counterpart.
 * Older compiler versions are considered first.
 * In Linux, GCC is iterated before Clang.

Currently, given the following supported platforms and configurations we
are generating **136 different binary packages for a C++ library**
and **88 for a C library**.

### Build Images

For more information see [conan-io/conan-docker-tools](https://github.com/conan-io/conan-docker-tools)

## Windows

- Python: 3.7.9
- CMake: 3.21.6
- WinSDK: 10.0.20348
- Compilers: Visual Studio:
  
  - 2017 (19.16.27048)
  - 2019 (19.29.30146)
  
- Release (MT/MD) and Debug (MTd, MDd)
- Architectures: x86_64
- Build types: Release, Debug
- Runtimes: MT/MD (Release), MTd/MDd (Debug)
- Options:
  - Shared, Static (option `"shared": [True, False]` in the recipe when available)
  - Header Only (option `"header_only": [True, False]` if available)

> :warning: The profile with the option `shared=True` and runtime `MT/MTd` is not built.

## Linux

- Python: 3.7.13
- CMake: 3.15.7, 3.18.2 (same version expected after all use [new docker images](https://github.com/conan-io/conan-docker-tools/tree/master/modern))
- Compilers:
  - GCC versions: 5, 7, 8, 9, 10, 11
  - Clang versions: 11, 12, 13
- C++ Standard Library (`libcxx`):
  - GCC compiler: `libstdc++`, `libstdc++11`
  - Clang compiler: `libstdc++`, `libc++`
- Architectures: x86_64
- Build types: Release, Debug
- Options:
  - Shared, Static (option `"shared": [True, False]` in the recipe when available)
  - Header Only (option `"header_only": [True, False]` is only added with the value True)

## MacOS

- Python: 3.7.12
- CMake: 3.20.1
- Compilers: Apple-clang versions 11.0.3, 12.0.5, 13.0.0
- C++ Standard Library (`libcxx`): `libc++`
- Architectures: x86_64, armv8
- Build types: Release, Debug
- Options:
  - Shared, Static (option ``"shared": [True, False]`` in the recipe when available)
  - Header Only (option `"header_only": [True, False]` is only added with the value True)
