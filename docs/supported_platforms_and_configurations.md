# Supported platforms and configurations

<!-- toc -->
## Contents

  * [Introduction](#introduction)
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


## Windows

- Compilers: Visual Studio:
  - 2015 (14.0.25431.01 Update 3)
  - 2017 (15.9.19+28307.1000)
  - 2019 (16.4.4+29728.190)
- Release (MT/MD) and Debug (MTd, MDd)
- Architectures: x86_64
- Build types: Release, Debug
- Runtimes: MT/MD (Release), MTd/MDd (Debug)
- Options:
  - Shared, Static (option `"shared": [True, False]` in the recipe when available)
  - Header Only (option `"header_only": [True, False]` is only added with the value True)

## Linux

- Compilers:
  - GCC versions 4.9, 5, 6, 7, 8, 9
  - Clang versions 3.9, 4.0, 5.0, 6.0, 7.0, 8, 9
- C++ Standard Library (`libcxx`):
  - GCC compiler: `libstdc++`, `libstdc++11`
  - Clang compiler: `libstdc++`, `libc++`
- Architectures: x86_64
- Build types: Release, Debug
- Options:
  - Shared, Static (option `"shared": [True, False]` in the recipe when available)
  - Header Only (option `"header_only": [True, False]` is only added with the value True)

## MacOS

- Compilers: Apple-clang versions 9.1, 10.0, 11.0 (three latest versions, we will rotate the older when a new compiler version is released)
- C++ Standard Library (`libcxx`): `libc++`
- Architectures: x86_64
- Build types: Release, Debug
- Options:
  - Shared, Static (option ``"shared": [True, False]`` in the recipe when available)
  - Header Only (option `"header_only": [True, False]` is only added with the value True)
