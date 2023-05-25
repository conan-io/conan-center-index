# Test Packages

This is the main way that ConanCenter is able to validate the contents of a package are valid.
It is required to provide a [`test_package/`](https://docs.conan.io/1/reference/commands/creator/create.html?highlight=test_package)
sub-directory with every recipe. These are expected to work regardless of the options or settings used as this is what consumer will encounter when doing a `conan create`
themselves. It's possible to have ConanCenter run `conan test` on more then one `test folder` by using the `test_` prefix.

<!-- toc -->
## Contents

  * [Files and Structure](#files-and-structure)
  * [CMake targets](#cmake-targets)
  * [Testing more generators with `test_<something>`](#testing-more-generators-with-test_something)
  * [Testing CMake variables from FindModules](#testing-cmake-variables-from-findmodules)
  * [How it works](#how-it-works)
  * [Minimalist Source Code](#minimalist-source-code)<!-- endToc -->

### Files and Structure

See the [recipe files and structures](README.md#recipe-files-structure) for a visual.

All ConanCenterIndex recipe should have a two [test_folders](https://docs.conan.io/1/reference/commands/creator/create.html?highlight=test_folder)
One for the current CMake generator in `test_package/`.

Please refer to the [Package Templates](../package_templates/) for the current practices about which files and what their content should be.

### CMake targets

When using CMake to test a package, the information should be consumed using the
[`CMakeDeps` generator](https://docs.conan.io/1/reference/conanfile/tools/cmake/cmakedeps.html?highlight=cmakedeps).

This typically will look like a `CMakeLists.txt` which contain lines similar to

```cmake
find_package(fmt REQUIRED CONFIG)
# ...
target_link_libraries(test_ranges PRIVATE fmt::fmt)
```

Refer to the [package template](https://github.com/conan-io/conan-center-index/blob/master/docs/package_templates/cmake_package/all/test_package/CMakeLists.txt) for more examples.

In ConanCenterIndex, we try to accurately represent the names of the targets and the information provided by CMake's modules and config files that some libraries
provide. If CMake or the library itself don't enforce any target name, the default ones provided by Conan should be recommended. The minimal project
in the `test_package` folder should serve as an example of the best way to consume the package, and targets are preferred over raw variables.

This rule applies for the _global_ target and for components ones. The following snippet should serve as example:

We encourage contributors to check that not only the _global_ target works properly, but also the ones for the components. It can be
done creating and linking different libraries and/or executables.

### Testing more generators with `test_<something>`

The CI will explore all the folders and run the tests for the ones matching `test_*/conanfile.py` pattern. You can find the output of all
of them together in the testing logs.

Sometimes it is useful to test the package using different build systems (CMake, Autotools,...). Instead of adding complex logic to one
`test_package/conanfile.py` file, it is better to add another `test_<something>/conanfile.py` file with a minimal example for that build system. That
way the examples will be short and easy to understand and maintain. In some other situations it could be useful to test different Conan generators
(e.g. `CMakeDeps`) using different folders and `conanfile.py` files.

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

### Testing CMake variables from FindModules

Recipes which provide [Find Modules](https://cmake.org/cmake/help/latest/manual/cmake-modules.7.html#find-modules) are strongly encouraged to
module the file name, targets and or variables.

**We will provide better docs in the near future**, for now here are a few references:

- Convo: https://github.com/conan-io/conan-center-index/pull/13511
- early example: https://github.com/conan-io/conan-center-index/tree/master/recipes/libxml2/all/test_cmake_module_package
- Best reference: https://github.com/conan-io/conan-center-index/blob/master/recipes/expat/all/test_package_module/CMakeLists.txt#L9

### How it works

The [build service](README.md#the-build-service) will explore all the folders and run the tests for the ones matching `test_*/conanfile.py` pattern.
You can find the output of all of them together in the testing logs. Only the end of the logs are posted even if an earlier "test folder" may have failed.

> **Note**: If, for any reason, it is useful to write a test that should only be checked using Conan v1, you can do so by using the pattern
> `test_v1_*/conanfile.py` for the folder. Please, have a look to [linter notes](../v2_linter.md) to know how to prevent the linter from
> checking these files.

Remember that the `test_<package>` recipes should **test the package configuration that has just been generated** for the _host_ context, otherwise
it will fail in cross-building scenarios; before running executables, recipes should check
[`conan.tools.build.can_run`](https://docs.conan.io/1/reference/conanfile/tools/build.html?highlight=can_run#conan-tools-build-can-run)

### Minimalist Source Code

The contents of `test_package.c` or `test_package.cpp` should be as minimal as possible, including a few headers at most with simple
instantiation of objects to ensure linkage and dependencies are correct. Any build system can be used to test the package, but
CMake or Meson are usually preferred.
