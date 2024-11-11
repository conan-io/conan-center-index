# Build and Package

This document gathers all the relevant information regarding the general lines to follow while writing either the `build()` or the `package()` methods.
Both methods often use build helpers to build binaries and install them into the `package_folder`.

<!-- toc -->
## Contents

  * [Build Method](#build-method)
  * [Package Method](#package-method)
  * [Build System Examples](#build-system-examples)
    * [Header Only](#header-only)
    * [CMake](#cmake)
    * [Autotools](#autotools)
    * [No Upstream Build Scripts](#no-upstream-build-scripts)
    * [System Packages](#system-packages)<!-- endToc -->

## Build Method

For the `build()` method, the general scope used to build artifacts. Please, read
the official reference to the [build()](https://docs.conan.io/2/reference/conanfile/methods/build.html) method and the
[Build packages: the build() method](https://docs.conan.io/2/tutorial/creating_packages/build_packages.html).

## Package Method

The `package()` method is used to copy the artifacts to the `package_folder`. Please, read the official reference to the
[package()](https://docs.conan.io/2/reference/conanfile/methods/package.html) method and the
[Package files: the package() method](https://docs.conan.io/2/tutorial/creating_packages/package_method.html).

## Build System Examples

The [Conan's documentation](https://docs.conan.io) is always a good place for technical details.
General patterns about how they can be used for OSS in ConanCenterIndex can be found in the
[package templates](../package_templates/README.md) sections. These are excellent to copy and start from.

### Header Only

If you are looking for header-only projects, you can take a look on [header-only template](../package_templates/header_only).
Also, Conan Docs have a section about [how to package header-only libraries](https://docs.conan.io/2/tutorial/creating_packages/other_types_of_packages/header_only_packages.html).

### CMake

For C/C++ projects which use CMake for building, you can take a look on [cmake package template](../package_templates/cmake_package).

### Autotools

There is an [autotools package template](../package_templates/autotools_package/) amiable to start from.

### No Upstream Build Scripts

For cases where a project only offers source files but does not provide a build script, you can add CMake support.
However, it is essential to first contact the upstream maintainers and open a pull request (PR) offering building support.
If your PR is rejected because the author does not want any kind of build script, or if the project is abandoned, Conan Center Index (CCI) will consider accepting your build script based on the effort required to maintain it, as we aim to avoid adding scripts that may require significant ongoing maintenance.
Take a look at [Bzip2](https://github.com/conan-io/conan-center-index/blob/master/recipes/bzip2/all/CMakeLists.txt) as example.

### System Packages

> **Note**: For exceptional cases where only system packages can be used and a regular Conan package may result in an incompatible and fragile package, a separated system package may be created. See the [FAQs](../faqs.md#can-i-install-packages-from-the-system-package-manager) for more.

The [package_manager](https://docs.conan.io/2/reference/tools/system/package_manager.html#conan-tools-system-package-manager) can easily manage a system package manager (e.g. apt,
pacman, brew, choco) and install packages which are missing on Conan Center but available for most distributions. It is key to correctly fill in the `cpp_info` for the consumers of a system package to have access to whatever was installed.

As example there is [xorg](https://github.com/conan-io/conan-center-index/blob/master/recipes/xorg/all/conanfile.py).