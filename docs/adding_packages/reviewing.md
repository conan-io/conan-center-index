# Reviewing policies

The following policies are preferred during the review, but not mandatory:

<!-- toc -->
## Contents

- [Reviewing policies](#reviewing-policies)
  - [Contents](#contents)
  - [CMake](#cmake)
    - [Caching Helper](#caching-helper)
    - [Build Folder](#build-folder)
    - [CMake Configure Method](#cmake-configure-method)
  - [Test Package](#test-package)
    - [Minimalistic Source Code](#minimalistic-source-code)
    - [CMake targets](#cmake-targets)

## Test Package

### Minimalistic Source Code

The contents of `test_package.c` or `test_package.cpp` should be as minimal as possible, including a few headers at most with simple
instantiation of objects to ensure linkage and dependencies are correct. Any build system can be used to test the package, but
CMake or Meson are usually preferred.

### CMake targets

When using CMake to test a package, the information should be consumed using the **targets provided by `cmake_find_package_multi` generator**. We
enforce this generator to align with the upcoming
[Conan's new `CMakeDeps` generator](https://docs.conan.io/en/latest/reference/conanfile/tools/cmake/cmakedeps.html?highlight=cmakedeps)
and it should help in the migration (and compatibility) with Conan v2.

In ConanCenter we try to mimic the names of the targets and the information provided by CMake's modules and config files that some libraries
provide. If CMake or the library itself don't enforce any target name, the ones provided by Conan should be recommended. The minimal project
in the `test_package` folder should serve as an example of the best way to consume the package, and targets are preferred over raw variables.

This rule applies for the _global_ target and for components ones. The following snippet should serve as example:

**CMakeLists.txt**
```cmake
cmake_minimum_required(VERSION 3.1.2)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(package REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} package::package)
```

We encourage contributors to check that not only the _global_ target works properly, but also the ones for the components. It can be
done creating and linking different libraries and/or executables.
