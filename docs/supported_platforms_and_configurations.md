# Supported platforms and configurations

<!-- toc -->
## Contents

  * [Introduction](#introduction)
    * [Future Steps](#future-steps)
  * [Windows](#windows)
  * [Linux](#linux)
  * [MacOS](#macos)<!-- endToc -->

## Introduction

The pipeline iterates a fixed list of profiles for every Conan reference,
it computes the packageID for each profile and discard duplicates. Then it
builds the packages for the remaining profiles and promoted them to
[JFrog ConanCenter](https://conan.io/center/) once the pull-request is merged.

Currently, given the following supported platforms and configurations we
are generating **30 different binary packages for a C++ library**.


### Future Steps

With the introduction of our new, more flexible pipeline,
we will be implementing several enhancements to improve our build capabilities and support
a wider range of development environments. The following steps will be taken:

- Incorporate additional modern GCC versions for Linux builds:
  - By adding the latest versions of GCC, we aim to ensure compatibility with the newest C++ standards and features, allowing developers to leverage the latest advancements in the language.
- Integrate more recent Clang versions for Linux builds:
  - Clang is known for its fast compilation times and excellent diagnostics. By including more modern versions, we will provide developers with improved performance and better error reporting, enhancing the overall development experience.
- Include updated Apple-Clang versions for macOS builds:
  - As macOS continues to evolve, it is crucial to support the latest Apple-Clang versions. This will ensure that our builds are optimized for the latest macOS features and provide a seamless experience for developers working in the Apple ecosystem.
- Add support for Android builds to the pipeline:
  - Expanding our pipeline to include Android builds will enable developers to create and test applications for mobile platforms more efficiently.
    This addition will help streamline the development process and ensure that our tools are versatile and adaptable to various environments.

## Windows

- Python: 3.7.9
- CMake: 3.21.6
- WinSDK: 10.0.20348
    > WinSDK version is rolled periodically as [discussed previously](https://github.com/conan-io/conan-center-index/issues/4450).
    > Please open an issue in case it needs to be updated.
- Compilers: Visual Studio:
  - 2019 (19.29.30148)

- Architectures: x86_64
- Build types: Release
- Runtime: dynamic (MD)
- Options:
  - Shared, Static (option `"*/*:shared": [True, False]` in the recipe when available)
  - Header Only (option `"&:header_only": [True, False]` is only added with the value True)

## Linux

- Python: 3.7.17
- CMake: 3.15.7, 3.18.6 (same version expected after all use [new docker images](https://github.com/conan-io/conan-docker-tools/tree/master/images))
- Compilers:
  - GCC versions: 11
- C++ Standard Library (`libcxx`):
  - GCC compiler: `libstdc++11`
- Architectures: x86_64
- Build types: Release
- Options:
  - Shared, Static (option `"*/*:shared": [True, False]` in the recipe when available)
  - Header Only (option `"&:header_only": [True, False]` is only added with the value True)

## MacOS

- Python: 3.7.12
- CMake: 3.20.1
- Compilers: Apple-clang versions 13.0.0
- Macos SDK versions (for each apple-clang version respectively): 11.3
- Macos deployment target (`minos`): 11.0
- C++ Standard Library (`libcxx`): `libc++`
- Architectures: armv8
- Build types: Release
- Options:
  - Shared, Static (option `"*/*:shared": [True, False]` in the recipe when available)
  - Header Only (option `"&:header_only": [True, False]` is only added with the value True)
