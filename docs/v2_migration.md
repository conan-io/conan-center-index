# Preparing recipes for Conan 2.0

This is expected for recipes to be updates in each pull request.

- Updated helpers are expected, this is enforced by the [v2_linter](v2_linter.md)
- Once a recipe publishes v2 packages, it must pass the v2 pipeline
- The v2 pipeline with **shortly be required** for changes to be merged.

<!-- toc -->
## Contents

  * [Using Layout](#using-layout)
    * [With New Generators](#with-new-generators)
    * [With Multiple Build Helpers](#with-multiple-build-helpers)
  * [CMakeToolchain](#cmaketoolchain)
  * [New conf_info properties](#new-conf_info-properties)
  * [New cpp_info set_property model](#new-cpp_info-set_property-model)
    * [Translating .names information to cmake_target_name, cmake_module_target_name and cmake_file_name](#translating-names-information-to-cmake_target_name-cmake_module_target_name-and-cmake_file_name)
    * [Translating .filenames information to cmake_file_name, cmake_module_file_name and cmake_find_mode](#translating-filenames-information-to-cmake_file_name-cmake_module_file_name-and-cmake_find_mode)
    * [Translating .build_modules to cmake_build_modules](#translating-build_modules-to-cmake_build_modules)
    * [PkgConfigDeps](#pkgconfigdeps)<!-- endToc -->

> **Note**: Read about the [linter in pull requests](v2_linter.md) to learn how this is being enforced.

It's time to start thinking seriously about Conan v2 and prepare recipes
for the incoming changes. Conan v2 comes with many
changes and improvements, you can read about them in the
[Conan documentation](https://docs.conan.io/1/conan_v2.html).

This document is a practical guide, offering extended information particular to Conan
Center Index recipes to get them ready to upgrade to Conan 2.0.

## Using Layout

All recipes should use a layout. Without one, more manual configuration of folders (e.g. source, build, etc)
and package structure will be required.

### With New Generators

When doing this there is no need to manually define `self._subfolder_[...]` in a recipe.
Simply use `self.source_folder` and `self.build_folder` instead of "subfolder properties" that used to be the norm.

### With Multiple Build Helpers

When different build tools are use, at least one layout needs to be set.

```python
    def layout(self):
        if self._use_cmake():
            cmake_layout(self)
        else: # using autotools
            basic_layout(self)
```

The `src_folder` must be the same when using different layouts and should
not depend on settings or options.

## CMakeToolchain

The old `CMake.definition` should be replaced by `CMakeToolchain.variables` and moved to the `generate` method.
However, certain options need to be passed as `cache_variables`. You'll need to check project's `CMakeLists.txt`
as there are a few cases to look out for:

- When an `option` is configured before `project()` is called.

  ```cmake
  cmake_minimum_required(3.1)
  option(BUILD_EXAMPLES "Build examples using foorbar")
  project(foobar)
  ```

- When an variable is declared with `CACHE`.

  ```cmake
  cmake_minimum_required(3.1)
  project(foobar)
  set(USE_JPEG ON CACHE BOOL "include jpeg support?")
  ```

For more information refere to the [CMakeToolchain docs](https://docs.conan.io/1/reference/conanfile/tools/cmake/cmaketoolchain.html)
or check out the converstaion in conan-io/conan#11937 for the brave.

## New conf_info properties

As described in the documentation `self.user_info` has been depreated and you are now required to use
`self.conf_info` to define individual properties to expose to downstream recipes.
The [2.0 migrations docs](https://docs.conan.io/1/migrating_to_2.0/recipes.html#removed-self-user-info)
should cover the technical details, however for ConanCenterIndex we need to make sure there are no collisions
`conf_info` must be named `user.<recipe_name>:<variable>`.

For usage options of `conf_info`, the [documenation](https://docs.conan.io/1/reference/config_files/global_conf.html?highlight=conf_info#configuration-in-your-recipes)

In ConanCenterIndex this will typically looks like:

- defining a value
  ```py
      def package_info(self):
          tool_path = os.path.join(self.package_folder, "bin", "tool")
          self.conf_info.define("user.pkg:tool", tool_path)
  ```
- using a value
  ```py
      #generators = "VirtualBuildEnv", "VirtualRunEnv"

      def build_requirements(self):
          self.tool_requires("tool/0.1")

      def build(self):
          tool_path = self.conf_info.get("user.pkg:tool")
          self.run(f"{tool_path} --build")
  ```

> **Note**: This should only be used when absolutely required. In the vast majority of cases, the new
> ["Environments"](https://docs.conan.io/1/reference/conanfile/tools/env/environment.html?highlight=Virtual)
> will include the `self.cpp_info.bindirs` which will provide access to the tools in the correct scopes.

## New cpp_info set_property model

New Conan generators like
[CMakeDeps](https://docs.conan.io/1/reference/conanfile/tools/cmake/cmakedeps.html)
and
[PkgConfigDeps](https://docs.conan.io/1/reference/conanfile/tools/gnu/pkgconfigdeps.html),
don't listen to `cpp_info`'s ``.names``, ``.filenames`` or ``.build_modules`` attributes.
There is a new way of setting the `cpp_info` information with these
generators using the ``set_property(property_name, value)`` method.

Both of these two models **will live together in recipes** to make
recipes compatible for both 1.x and 2.0 users. Deprecated feilds are not to be removed at this time.

To understand the impact of these and the relation between different generates, refer to the 
[migrating properties](https://docs.conan.io/1/migrating_to_2.0/properties.html) documentation.

### Translating .names information to cmake_target_name, cmake_module_target_name and cmake_file_name

The variation of `names` is covered by the [Conan documentation](https://docs.conan.io/1/migrating_to_2.0/properties.html#migrating-from-names-to-cmake-target-name).

### Translating .filenames information to cmake_file_name, cmake_module_file_name and cmake_find_mode

As for `filenames`, refer to [this section](https://docs.conan.io/1/migrating_to_2.0/properties.html#migrating-from-filenames-to-cmake-file-name).

### Translating .build_modules to cmake_build_modules

The variation of `build_modules` is covered by the [Conan documentation](https://docs.conan.io/1/migrating_to_2.0/properties.html#translating-build-modules-to-cmake-build-modules).

### PkgConfigDeps

For migrating, `names` used with `pkg_config`, see [Conan documentation](https://docs.conan.io/1/migrating_to_2.0/properties.html#migration-from-names-to-pkg-config-name)
