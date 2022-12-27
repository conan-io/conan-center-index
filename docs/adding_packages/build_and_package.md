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

* `build()` method should focus on build only, not installation. During the build, nothing should be written in `package` folder. Installation step should only occur in `package()` method.

* The build itself should only rely on local files. Nothing should be downloaded from the internet during this step. If external files are required, they should come from `requirements` or `build_requirements` in addition to source files downloaded in `source()` or coming from the recipe itself.

* Except for CMake and a working build toolchain (compiler, linker, archiver, etc.), the recipe should not assume that any other build tool is installed on the user-build machine (like Meson, autotools, or pkg-config). On Windows, the recipe should not assume that a shell is available (like MSYS2). Therefore, if the build method requires additional tools, they should be added to `build_requirements()`.

* It is forbidden to run other conan client commands during build. In other words, if upstream build files call conan under the hood (through `cmake-conan` for example or any other logic), this logic must be removed.

* Settings from profile should be honored (`build_type`, `compiler.libcxx`, `compiler.cppstd`, `compiler.runtime` etc).

* These env vars from profile should be honored and properly propagated to underlying build system during the build: `CC`, `CXX`, `CFLAGS`, `CXXFLAGS`, `LDFLAGS`.

## Package Method

* CMake config files must be removed (they will be generated for consumers by `cmake_find_package`, `cmake_find_package_multi`, or `CMakeDeps` generators). Use `rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))` or `rm(self, "*.cmake", os.path.join(self.package_folder, "lib"))`.

* pkg-config files must be removed (they will be generated for consumers by `pkg_config` or `PkgConfigDeps` generators). Use `rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))` or `rm(self, "*.pc", os.path.join(self.package_folder, "lib"))`.

* On *nix systems, executables and shared libraries should have empty `RPATH`/`RUNPATH`/`LC_RPATH`.

* On macOS, install name in `LC_ID_DYLIB` section of shared libs must be `@rpath/<libfilename>`.

* Installed files must not contain absolute paths specific to build machine. Relative paths to other packages is also forbidden since relative paths of dependencies during build may not be the same for consumers. Hardcoded relative paths pointing to a location in the package itself are allowed.

## Build System Examples

The [Conan's documentation](https://docs.conan.io) is always a good place for technical details.
General patterns about how they can be used for OSS in ConanCenterIndex can be found in the
[package templates](../package_templates/README.md) sections. These are excellent to copy and start from.

### Header Only

If you are looking for header-only projects, you can take a look on [header-only template](../package_templates/header_only).
Also, Conan Docs have a section about [how to package header-only libraries](https://docs.conan.io/en/latest/howtos/header_only.html).

### CMake

For C/C++ projects which use CMake for building, you can take a look on [cmake package template](../package_templates/cmake_package).

Another common use case for CMake based projects, both header only and compiled, is _modeling components_ to match the `find_package` and export the correct targets from Conan's generators. A basic examples of this is [cpu_features](https://github.com/conan-io/conan-center-index/blob/master/recipes/cpu_features/all/conanfile.py), a moderate/intermediate example is [cpprestsdk](https://github.com/conan-io/conan-center-index/blob/master/recipes/cpprestsdk/all/conanfile.py), and a very complex example is [OpenCV](https://github.com/conan-io/conan-center-index/blob/master/recipes/opencv/4.x/conanfile.py).

### Autotools

There is an [autotools package template](../package_templates/autotools_package/) amiable to start from.

However, if you need to use autotools for building, you can take a look on [libalsa](https://github.com/conan-io/conan-center-index/blob/master/recipes/libalsa/all/conanfile.py), [kmod](https://github.com/conan-io/conan-center-index/blob/master/recipes/kmod/all/conanfile.py), [libcap](https://github.com/conan-io/conan-center-index/blob/master/recipes/libcap/all/conanfile.py).

Many projects offer [**pkg-config**'s](https://www.freedesktop.org/wiki/Software/pkg-config/) `*.pc` files which need to be modeled using components. A prime example of this is [Wayland](https://github.com/conan-io/conan-center-index/blob/master/recipes/wayland/all/conanfile.py).

### No Upstream Build Scripts

For cases where a project only offers source files, but not a build script, you can add CMake support, but first, contact the upstream and open a PR offering building support. If it's rejected because the author doesn't want any kind of build script, or the project is abandoned, CCI can accept your build script. Take a look at [Bzip2](https://github.com/conan-io/conan-center-index/blob/master/recipes/bzip2/all/CMakeLists.txt) and [DirectShowBaseClasses](https://github.com/conan-io/conan-center-index/blob/master/recipes/directshowbaseclasses/all/CMakeLists.txt) as examples.

### System Packages

> **Note**: For exceptional cases where only system packages can be used and a regular Conan package may result in an incompatible and fragile package, a separated system package may be created. See the [FAQs](../faqs.md#can-i-install-packages-from-the-system-package-manager) for more.

The [SystemPackageTool](https://docs.conan.io/en/latest/reference/conanfile/methods.html#systempackagetool) can easily manage a system package manager (e.g. apt,
pacman, brew, choco) and install packages which are missing on Conan Center but available for most distributions. It is key to correctly fill in the `cpp_info` for the consumers of a system package to have access to whatever was installed.

As example there is [xorg](https://github.com/conan-io/conan-center-index/blob/master/recipes/xorg/all/conanfile.py). Also, it will require an exception rule for [conan-center hook](https://github.com/conan-io/hooks#conan-center), a [pull request](https://github.com/conan-io/hooks/pulls) should be open to allow it over the KB-H032.
