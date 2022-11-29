# Test Packages

the test package is how ConanCenter is able to validate the contents of packages are valid. This involves installing, generating, compiling, and linking any artifacts.

It's encourages to test multiple options and setting in the default `test_package/` since that is what's used by consumers building locally from source.

<!-- toc -->
## Contents

    * [Files and Structure](#files-and-structure)
    * [CMake targets](#cmake-targets)
      * [CMakeLists.txt](#cmakeliststxt)
      * [V1 CMakeLists.txt](#v1-cmakeliststxt)
      * [Testing more generators with `test_<something>`](#testing-more-generators-with-test_something)
    * [Minimalist Source Code](#minimalist-source-code)<!-- endToc -->

### Files and Structure

A Complete folder structure (including the [V2 Migration](../v2_migration.md)) looks as follows

```
.
+-- recipes
|   +-- library_name/
|       +-- config.yml
|       +-- all/
|           +-- conanfile.py
|           +-- conandata.yml
|           +-- patches/
|               +-- add-missing-string-header-2.0.0.patch
|           +-- test_package/
|               +-- conanfile.py
|               +-- CMakeLists.txt
|               +-- test_package.cpp
|           +-- test_v1_package/
|               +-- conanfile.py
|               +-- CMakeLists.txt
```

### CMake targets

When using CMake to test a package, the information should be consumed using the new
[`CMakeDeps` generator](https://docs.conan.io/en/latest/reference/conanfile/tools/cmake/cmakedeps.html?highlight=cmakedeps). It's
still important to test targets provided by `cmake_find_package_multi` generator. It should help in the migration (and compatibility) with Conan v2.

In ConanCenter we try to accurately represent the names of the targets and the information provided by CMake's modules and config files that some libraries
provide. If CMake or the library itself don't enforce any target name, the default ones provided by Conan should be recommended. The minimal project
in the `test_package` folder should serve as an example of the best way to consume the package, and targets are preferred over raw variables.

This rule applies for the _global_ target and for components ones. The following snippet should serve as example:

We encourage contributors to check that not only the _global_ target works properly, but also the ones for the components. It can be
done creating and linking different libraries and/or executables.

#### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(package REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE package::package)
```

#### V1 CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.1.2)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(package REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} package::package)
```

#### Testing more generators with `test_<something>`

The CI will explore all the folders and run the tests for the ones matching `test_*/conanfile.py` pattern. You can find the output of all
of them together in the testing logs.

Sometimes it is useful to test the package using different build systems (CMake, Autotools,...). Instead of adding complex logic to one
`test_package/conanfile.py` file, it is better to add another `test_<something>/conanfile.py` file with a minimal example for that build system. That
way the examples will be short and easy to understand and maintain. In some other situations it could be useful to test different Conan generators
(`cmake_find_package`, `CMakeDeps`,...) using different folders and `conanfile.py` files ([see example](https://github.com/conan-io/conan-center-index/tree/master/recipes/fmt/all)).

When using more than one `test_<something>` folder, create a different project for each of them to keep the content of the `conanfile.py` and the
project files as simple as possible, without the need of extra logic to handle different scenarios.

```
.
+-- recipes
|   +-- library_name/
|       +-- config.yml
|       +-- all/
|           +-- ...
|           +-- test_package/
|               +-- ...
|           +-- test_cmakedeps/
|               +-- conanfile.py
|               +-- CMakeLists.txt
|               +-- test_package.cpp
```

### Minimalist Source Code

The contents of `test_package.c` or `test_package.cpp` should be as minimal as possible, including a few headers at most with simple
instantiation of objects to ensure linkage and dependencies are correct. Any build system can be used to test the package, but
CMake or Meson are usually preferred.
