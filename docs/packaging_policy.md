# Packaging Policy

This document gathers all the relevant information regarding the general lines to follow while creating new recipes that will eventually be part of this repository.

<!-- toc -->
## Contents

  * [Sources](#sources)
  * [Dependencies](#dependencies)
  * [Build](#build)
  * [Package](#package)
  * [Settings](#settings)
  * [Options](#options)<!-- endToc -->

## Sources

**Origin of sources:**

* Library sources should come from an official origin like the library source code repository or the official
release/download webpage.

* If an official source archive is available, it should be preferred over an auto-generated archive.

**Source immutability:** Downloaded source code stored under `source` folder should not be modified. Any patch should be applied to the copy of this source code when a build is executed (basically in `build()` method).

**Building from sources:** Recipes should always build packages from library sources.

**Sources not accessible:**

* Library sources that are not publicly available will not be allowed in this repository even if the license allows their redistribution.

* If library sources cannot be downloaded from their official origin or cannot be consumed directly due to their
  format, the recommendation is to contact the publisher and ask them to provide the sources in a way/format that can be consumed
  programmatically.

* In case of needing those binaries to use them as a "build require" for some library, we will consider following the approach of adding it
  as a system recipe (`<build_require>/system`) and making those binaries available in the CI machines (if the license allows it).

## Dependencies

* Version range is not allowed.

* Specify explicit RREV (recipe revision) of dependencies is not allowed.

* Vendoring in library source code should be removed (best effort) to avoid potential ODR violations. If upstream takes care to rename symbols, it may be acceptable.

* Only other conan-center recipes are allowed in `requires`/`requirements()` and `build_requires`/`build_requirements()` of a conan-center recipe.

* If a requirement is conditional, this condition must not depend on build context. Build requirements don't have this constraint.

* Forcing options of dependencies inside a conan-center recipe should be avoided, except if it is mandatory for the library.

## Build

* `build()` method should focus on build only, not installation. During the build, nothing should be written in `package` folder. Installation step should only occur in `package()` method.

* The build itself should only rely on local files. Nothing should be downloaded from internet during this step. If external files are required, they should come from `requirements` or `build_requirements`, in addition to source files downloaded in `source()` or coming from recipe itself.

* Except CMake and a working build toolchain (compiler, linker, archiver etc), the recipe should not assume that any other build tool is installed on user build machine (like Meson, autotools or pkg-config). On Windows, recipe should not assume that a shell is available (like MSYS2). Therefore, if the buid requires additional build tools, they should be added to `build_requirements()`.

* It is forbidden to run other conan client commands during build. In other words, if upstream build files call conan under the hood (through `cmake-conan` for example or any other logic), this logic must be neutralized.

* Settings from profile should be honored (`build_type`, `compiler.libcxx`, `compiler.cppstd`, `compiler.runtime` etc).

* These env vars from profile should be honored and properly propagated to underlying build system during the build: `CC`, `CXX`, `CFLAGS`, `CXXFLAGS`, `LDFLAGS`.

## Package

* CMake config files must be removed (they will be generated for consumers by `cmake_find_package`, `cmake_find_package_multi` or `CMakeDeps` generators).

* pkg-config files must be removed (they will be generated for consumers by `pkg_config` or `PkgConfigDeps` generators).

* On *nix systems, executables and shared libraries should have empty `RPATH`/`RUNPATH`/`LC_RPATH`.

* On macOS, install name in `LC_ID_DYLIB` section of shared libs must be `@rpath/<libfilename>`.

* Installed files must not contain absolute paths specific to build machine. Relative paths to other packages is also forbidden since relative paths of dependencies during build may not be the same for consumers. Hardcoded relative paths pointing to a location in the package itself are allowed.

## Settings

All recipes should list the four settings `os`, `arch`, `compiler` and `build_type` so Conan will compute a different package ID
for each combination. There are some particular cases for this general rule:

* **Recipes for _header only_ libraries** might omit the `settings` attibute, but in any case they should add

   ```python
   def package_id(self):
      self.info.header_only()
   ```

* **Recipes that provide applications** (`b2`, `cmake`, `make`,...) that are generally used as a _build requires_, must list all
   the settings as well, but they should remove the `compiler` one in the corresponding method unless the recipe provides also
   libraries that are consumed by other packages:

   ```python
   def package_id(self):
      del self.info.settings.compiler
   ```

   Removing the `compiler` setting reduces the number of configurations generated by the CI, reducing the time and workload and, at the
   same time, demonstrates the power of Conan behind the package ID logic.

   > Note.- Intentionally, the `build_type` setting should not be removed from the package ID in this case. Preserving this
   > setting will ensure that the package ID for Debug and Release configurations will be different and both binaries can be
   > available in the Conan cache at the same time. This enable consumers to switch from one configuration to the other in the case
   > they want to run or to debug those executables.

## Options

Recipes can list any number of options with any meaning, and defaults are up to the recipe itself. The CI cannot enforce anything
in this direction. However, there are a couple of options that have a special meaning for the CI.

### Predeinfed Options and Known Defaults

ConanCenter supports many combinations, these are outline in the [supported configurations](supported_platforms_and_configurations.md) document for each platform. 

* `shared` (with values `True` or `False`). The CI inspects the recipe looking for this option. The **default should be `shared=False`** and will
   generate all the configurations with values `shared=True` and `shared=False`.

   > **Note**: The CI applies `shared=True` only to the package being built, while every other requirement will. It's important to keep this in mind when trying to consume shared packages from ConanCenter.
   > It's important to keep this in mind when trying to consume shared packages from ConanCenter
   > as their requirements were linked inside the shared library. See [FAQs](faqs.md#how-to-consume-a-graph-of-shared-libraries) for more information.

* `fPIC` (with values `True` or `False`). The **default should be `fPIC=True`** and will generate all the configurations with values `fPIC=True` and `fPIC=False`.
  This option does not make sense on all the support configurations so it should be be removed.

   ```python
   def config_options(self):
       if self.settings.os == "Windows":
      del self.options.fPIC

   def configure(self):
      if self.options.shared:
         try:
             del self.options.fPIC
         except Exception:
             pass
   ```

* `header_only` (with values `True` or `False`). The **default should be `header_only=False`**. If the CI detects this option, it will generate all the
   configurations for the value `header_only=False` and add one more configuration with `header_only=True`. **Only one package**
   will be generated for `header_only=True`, so it is crucial that the package is actually a _header only_ library, with header files only (no libraries or executables inside).

   Recipes with such option should include the following in their `package_id` method

   ```python
   def package_id(self):
      if self.options.header_only:
         self.info.clear()
   ```

   ensuring that, when the option is active, the recipe ignores all the settings and only one package ID is generated.

### Options to Avoid

* `build_testing` should not be added, nor any other related unit test option. Options affect the package ID, therefore, testing should not be part of that.
   Instead, use Conan config [skip_test](https://docs.conan.io/en/latest/reference/config_files/global_conf.html#tools-configurations) feature:

   ```python
   def _configure_cmake(self):
      cmake = CMake(self)
      cmake.definitions['BUILD_TESTING'] = not self.conf.get("tools.build:skip_test", default=true, check_type=bool)
   ```

   The `skip_test` configuration is supported by [CMake](https://docs.conan.io/en/latest/reference/build_helpers/cmake.html#test) and [Meson](https://docs.conan.io/en/latest/reference/build_helpers/meson.html#test).

### Recommended feature options names

It's often needed to add options to toggle specific library features on/off. Regardless of the default, there is a strong preference for using positive naming for options. In order to avoid the fragmentation, we recommend to use the following naming conventions for such options:

- enable_<feature> / disable_<feature>
- with_<dependency> / without_<dependency>
- use_<feature>

the actual recipe code then may look like:

```py
    options = {"use_tzdb": [True, False]}
    default_options = {"use_tzdb": True}
```

```py
    options = {"enable_locales": [True, False]}
    default_options = {"enable_locales": True}
```

```py
    options = {"with_zlib": [True, False]}
    default_options = {"with_zlib": True}
```

having the same naming conventions for the options may help consumers, e.g. they will be able to specify options with wildcards: `-o *:with_threads=True`, therefore, `with_threads` options will be enabled for all packages in the graph that support it.
