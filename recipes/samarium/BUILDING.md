# Building with CMake

## For users

See [README.md](README.md)

## For Devs

### About

Samarium uses CMake for building. Building using other methods is not supported
Samarium uses Conan for dependency management, but can use native Find*.cmake. However the latter requires manual installation of libraries.

### Dependencies

No manual dependency management is required as it is handled through [Conan](https://conan.io).

For a list of dependencies, please refer to [conanfile.txt](conanfile.txt).

### Build

Samarium uses [CMake Presets](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html) to make building easy

```sh
cmake --preset=dev
cmake --build --preset=default
```

<!-- ## Install

This project doesn't require any special command-line flags to install to keep
things simple. As a prerequisite, the project has to be built with the above
commands already.

The below commands require at least CMake 3.15 to run, because that is the
version in which [Install a Project][1] was added.

Here is the command for installing the release mode artifacts with a
single-configuration generator, like the Unix Makefiles one:

```sh
cmake --install build
```

Here is the command for installing the release mode artifacts with a
multi-configuration generator, like the Visual Studio ones:

```sh
cmake --install build --config Release
```

### CMake package

This project exports a CMake package to be used with the [`find_package`][2]
command of CMake:

* Package name: `temp`
* Target name: `temp::temp`

Example usage:

```cmake
find_package(temp REQUIRED)
# Declare the imported target as a build requirement using PRIVATE, where
# project_target is a target created in the consuming project
target_link_libraries(
    project_target PRIVATE
    temp::temp
)
``` -->

[1]: https://cmake.org/cmake/help/latest/manual/cmake.1.html#install-a-project
[2]: https://cmake.org/cmake/help/latest/command/find_package.html
