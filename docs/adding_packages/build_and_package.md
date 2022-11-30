# Build and Package

This document gathers all the relevant information regarding the general lines to follow while writing either the `build()` or the `package()` methods.
Both methods often use build helpers to build binaries and install them into the `package_folder`.

<!-- toc -->
## Contents

  * [Build Method](#build-method)
  * [Package](#package)<!-- endToc -->

## Build Method

* `build()` method should focus on build only, not installation. During the build, nothing should be written in `package` folder. Installation step should only occur in `package()` method.

* The build itself should only rely on local files. Nothing should be downloaded from the internet during this step. If external files are required, they should come from `requirements` or `build_requirements` in addition to source files downloaded in `source()` or coming from the recipe itself.

* Except for CMake and a working build toolchain (compiler, linker, archiver, etc.), the recipe should not assume that any other build tool is installed on the user-build machine (like Meson, autotools, or pkg-config). On Windows, the recipe should not assume that a shell is available (like MSYS2). Therefore, if the build method requires additional tools, they should be added to `build_requirements()`.

* It is forbidden to run other conan client commands during build. In other words, if upstream build files call conan under the hood (through `cmake-conan` for example or any other logic), this logic must be removed.

* Settings from profile should be honored (`build_type`, `compiler.libcxx`, `compiler.cppstd`, `compiler.runtime` etc).

* These env vars from host profile (`[env]` for conan v1 recipes, `[buildenv]` for conan v2 recipes) should be honored and properly propagated to underlying build system during the build: `CC`, `CXX`, `AR` `LD`. They should be curated on the fly if underlying build system expects a specific format (no spaces in path, forward slash instead of back slash, etc).

* These compiler and linker conf from host profile should be honored and propagated to underlying build system during the build:
  * `tools.build:cflags`
  * `tools.build:cxxflags`
  * `tools.build:defines`
  * `tools.build:sharedlinklags`
  * `tools.build:exelinkflags`
  * `tools.apple:enable_bitcode` (only if host OS is `iOS`/`watchOS`/`tvOS`)

* If host OS is Apple OS family (`macOS`/`iOS`/`watchOS`/`tvOS`), `-headerpad_max_install_names` flag should be passed to linker, except if host OS is `iOS`/`watchOS`/`tvOS` and `tools.apple:enable_bitcode` is enabled.

* Multithread build (if supported by underlying build system):
  * if some steps are sensitive to race conditions, monothread should be enforced.
  * otherwise multithreaded build should be enabled with a number of cores controlled by `tools.build:jobs` conf from host profile if it is set, otherwise to all cores of build machine.

## Package

* CMake config files must be removed (they will be generated for consumers by `cmake_find_package`, `cmake_find_package_multi`, or `CMakeDeps` generators). Use `rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))` or `rm(self, "*.cmake", os.path.join(self.package_folder, "lib"))`.

* pkg-config files must be removed (they will be generated for consumers by `pkg_config` or `PkgConfigDeps` generators). Use `rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))` or `rm(self, "*.pc", os.path.join(self.package_folder, "lib"))`.

* On *nix systems, executables and shared libraries should have empty `RPATH`/`RUNPATH`/`LC_RPATH`.

* On macOS, install name in `LC_ID_DYLIB` section of shared libs must be `@rpath/<libfilename>`.

* Installed files must not contain absolute paths specific to build machine. Relative paths to other packages is also forbidden since relative paths of dependencies during build may not be the same for consumers. Hardcoded relative paths pointing to a location in the package itself are allowed.
