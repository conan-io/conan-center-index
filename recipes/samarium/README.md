# Samarium

[![GCC](https://github.com/strangeQuark1041/samarium/actions/workflows/gcc.yml/badge.svg)](https://github.com/strangeQuark1041/samarium/actions/workflows/gcc.yml)
[![Clang](https://github.com/strangeQuark1041/samarium/actions/workflows/clang.yml/badge.svg)](https://github.com/strangeQuark1041/samarium/actions/workflows/clang.yml)
[![MSVC](https://github.com/strangeQuark1041/samarium/actions/workflows/msvc.yml/badge.svg)](https://github.com/strangeQuark1041/samarium/actions/workflows/msvc.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=strangeQuark1041_samarium&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=strangeQuark1041_samarium)

![Lines of Code](https://img.shields.io/tokei/lines/github/strangeQuark1041/samarium)
![Repo Size](https://img.shields.io/github/repo-size/strangeQuark1041/samarium)
[![MIT License](https://img.shields.io/badge/license-MIT-yellow)](https://github.com/strangeQuark1041/samarium/blob/main/LICENSE.md)
![language: C++20](https://img.shields.io/badge/language-C%2B%2B20-yellow)

Samarium is a 2d physics simulation library written in modern C++20.

## Contents

- [Contents](#contents)
- [Quickstart](#quickstart)
- [Prerequistes](#prerequistes)
- [Installation](#installation)
- [Example](#example)
- [Tools](#tools)
- [Documentation](#documentation)
- [License](#license)
- [References](#references)

## Quickstart

```sh
pip install conan
git clone --depth 1 https://github.com/strangeQuark1041/samarium.git
conan create samarium -b missing
```

## Prerequistes

| Dependency | URL | Documentation |
| ---        | --- | --- |
| python     | <https://www.python.org/downloads/> | <https://www.python.org/doc/> |
| git        | <https://git-scm.com/downloads/> | <https://git-scm.com/docs/> |
| cmake      | <https://cmake.org/download/> | <https://cmake.org/cmake/help/latest/> |
| conan      | <https://conan.io/downloads.html/> | <https://docs.conan.io/en/latest/> |

A compiler supporting C++20 is required, namely GCC-11, Clang-13, or Visual C++ 2019

## Installation

To install the library locally:

```sh
git clone --depth 1 https://github.com/strangeQuark1041/samarium.git
conan create samarium -b missing
```

## Example

For a fully-featured and self-contained example, run:

```sh
git clone --depth 1 https://github.com/strangeQuark1041/samarium_example.git .
conan install . -b missing -if ./build # Install deps in build folder
cmake -B ./build
cmake --build ./build
./build/bin/example
```

## Tools

For the optimal developing experience, use [VSCode](https://code.visualstudio.com) using the following extensions and tools

1. [C++ Extension Pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools-extension-pack)
2. [Clang Format](https://clang.llvm.org/docs/ClangFormat.html)
3. [CMake Format](https://github.com/cheshirekow/cmake_format) and the corresponding [extension](https://marketplace.visualstudio.com/items?itemName=cheshirekow.cmake-format)
4. [SonarLint](https://marketplace.visualstudio.com/items?itemName=SonarSource.sonarlint-vscode)
5. [C++ Advanced Lint](https://marketplace.visualstudio.com/items?itemName=jbenden.c-cpp-flylint)

## Documentation

Documentation is located at [Github Pages](https://strangequark1041.github.io/samarium/)

For development, see [BUILDING.md](BUILDING.md)

## License

Samarium is distributed under the permissive [MIT License](LICENSE.md).

## References

These sources were of invaluable help during development:

1. C++ Standard: <https://en.cppreference.com/>
2. Custom iterators: <https://internalpointers.com/post/writing-custom-iterators-modern-cpp>
