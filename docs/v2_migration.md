# Preparing recipes for Conan 2.0

Refer to [road to Conan v2](v2_roadmap.md) to know the steps that
will be taken in ConanCenter and this repository to start running
Conan v2 in pull requests.

<!-- toc -->
## Contents

  * [Using Layout](#using-layout)
    * [With New Generators](#with-new-generators)
    * [With Multiple Build Helpers](#with-multiple-build-helpers)
  * [CMakeToolchain](#cmaketoolchain)
  * [New conf_info properties](#new-conf_info-properties)
  * [New cpp_info set_property model](#new-cpp_info-set_property-model)
    * [CMakeDeps](#cmakedeps)
    * [Update required_conan_version to ">=1.43.0"](#update-required_conan_version-to-1430)
    * [Translating .names information to cmake_target_name, cmake_module_target_name and cmake_file_name](#translating-names-information-to-cmake_target_name-cmake_module_target_name-and-cmake_file_name)
    * [Translating .filenames information to cmake_file_name, cmake_module_file_name and cmake_find_mode](#translating-filenames-information-to-cmake_file_name-cmake_module_file_name-and-cmake_find_mode)
    * [Understanding some workarounds with the .names attribute model in recipes](#understanding-some-workarounds-with-the-names-attribute-model-in-recipes)
    * [Translating .build_modules to cmake_build_modules](#translating-build_modules-to-cmake_build_modules)
    * [PkgConfigDeps](#pkgconfigdeps)<!-- endToc -->

> **Note**: Read about the [linter in pull requests](v2_linter.md) to learn how this is being enforced.

It's time to start thinking seriously about Conan v2 and prepare recipes
for the incoming changes. Conan v2 comes with many
changes and improvements, you can read about them in the
[Conan documentation](https://docs.conan.io/en/latest/conan_v2.html).

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

For more information refere to the [CMakeToolchain docs](https://docs.conan.io/en/latest/reference/conanfile/tools/cmake/cmaketoolchain.html)
or check out the converstaion in conan-io/conan#11937 for the brave.

## New conf_info properties

As described in the documentation `self.user_info` has been depreated and you are now required to use
`self.conf_info` to define individual properties to expose to downstream recipes.
The [2.0 migrations docs](https://docs.conan.io/en/latest/migrating_to_2.0/recipes.html#removed-self-user-info)
should cover the technical details, however for ConanCenterIndex we need to make sure there are no collisions
`conf_info` must be named `user.<recipe_name>:<variable>`.

For usage options of `conf_info`, the [documenation](https://docs.conan.io/en/latest/reference/config_files/global_conf.html?highlight=conf_info#configuration-in-your-recipes)

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
> ["Environments"](https://docs.conan.io/en/latest/reference/conanfile/tools/env/environment.html?highlight=Virtual)
> will include the `self.cpp_info.bindirs` which will provide access to the tools in the correct scopes.

## New cpp_info set_property model

New Conan generators like
[CMakeDeps](https://docs.conan.io/en/latest/reference/conanfile/tools/cmake/cmakedeps.html)
and
[PkgConfigDeps](https://docs.conan.io/en/latest/reference/conanfile/tools/gnu/pkgconfigdeps.html),
don't listen to *cpp_info* ``.names``, ``.filenames`` or ``.build_modules`` attributes.
There is a new way of setting the *cpp_info* information with these
generators using the ``set_property(property_name, value)`` method.

All the information in the recipes, already set with the current model, should be
translated to the new model. These two models **will live together in recipes** to make
recipes compatible **with both new and current generators** for some time. After a stable
Conan 2.0 version is released, and when the moment arrives that we don't support the
current generators anymore in Conan Center Index, those attributes (``.names``,
``.filenames`` etc.) will disappear from recipes, and only ``set_property`` methods will
stay.

We will cover some cases of porting all the information set with the current model to the
new one. To read more about the properties available for each generator and how the
properties model work, please check the [Conan documentation](https://docs.conan.io/en/latest/conan_v2.html#editables-don-t-use-external-templates-any-more-new-layout-model).

> **Note**: Please, remember that the **new** ``set_property`` and the **current** attributes
> model are *completely independent since Conan 1.43*. Setting ``set_property`` in recipes will
> not affect current CMake 1.X generators (``cmake``, ``cmake_multi``, ``cmake_find_package`` and
> ``cmake_find_package_multi``) at all.

### CMakeDeps

### Update required_conan_version to ">=1.43.0"

If you set the property ``cmake_target_name`` in the recipe, the Conan minimum
required version should be updated to 1.43.

```python

required_conan_version = ">=1.43.0"

class GdalConan(ConanFile):
    name = "gdal"
    ...
```

The reason for this change is that in Conan versions previous to 1.43 the
``cmake_target_name`` values were not the final CMake target names. Those values were
completed by Conan, adding namespaces automatically the final target names. After 1.43
``cmake_target_name`` sets the **complete target name** that is added to the ``.cmake``
files generated by Conan. Let's see an example:

```python
class GdalConan(ConanFile):
    name = "gdal"
    ...
    def package_info(self):
        # Before 1.43 -> Conan adds GDAL:: namespace -> Creates target with name GDAL::GDAL
        # self.cpp_info.set_property("cmake_target_name", "GDAL")

        # After 1.43 -> Conan creates target with name GDAL::GDAL
        self.cpp_info.set_property("cmake_target_name", "GDAL::GDAL")
```

### Translating .names information to cmake_target_name, cmake_module_target_name and cmake_file_name

To translate the ``.names`` information to the new model there are some important things to
take into account:

* The value of the ``.names`` attribute value in recipes is just a part of the final
  target name for CMake generators. Conan will complete the rest of the target name by
  pre-pending a namespace (with ``::`` separator) to the ``.names`` value. This namespace takes
  the same value as the ``.names`` value. Let's see an example:

```python
class SomePkgConan(ConanFile):
    name = "somepkg"
    ...
    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "some-pkg"
        self.cpp_info.names["cmake_find_package_multi"] = "some-pkg"
        ...
```

This recipe generates the target ``some-pkg::some-pkg`` for both the
``cmake_find_package`` and the ``cmake_find_package_multi`` generators. Also, please
remember that if no ``.names`` attribute were set, Conan would create the target
``somepkg::somepkg`` for both generators by default.

As we explained before, the ``cmake_target_name`` sets the **complete target name**, so,
to translate this information to the new model we should add the following lines:

```python
class SomePkgConan(ConanFile):
    name = "somepkg"
    ...
    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "some-pkg"
        self.cpp_info.names["cmake_find_package_multi"] = "some-pkg"
        # CMakeDeps does NOT add any namespace automatically
        self.cpp_info.set_property("cmake_target_name", "some-pkg::some-pkg")
        ...
```

* If ``.filenames`` attribute is not set, it will fall back on the ``.names`` value to
  generate the files. Both the ``Find<pkg>.cmake`` and ``<pkg>-config.cmake`` files that
  store the dependencies will take the ``.names`` value to create the complete filename.
  For the previous example, to translate all the information from the current model to the
  new one, we should have added one more line setting the ``cmake_file_name`` value.

```python
class SomePkgConan(ConanFile):
    name = "somepkg"
    ...
    def package_info(self):
        # These generators fallback the filenames for the .cmake files
        # in the .names attribute value and generate
        self.cpp_info.names["cmake_find_package"] = "some-pkg" # generates module file Findsome-pkg.cmake
        self.cpp_info.names["cmake_find_package_multi"] = "some-pkg" # generates config file some-pkg-config.cmake

        self.cpp_info.set_property("cmake_target_name", "some-pkg::some-pkg")
        self.cpp_info.set_property("cmake_file_name", "some-pkg") # generates config file some-pkg-config.cmake
        ...
```

Please note that if we hadn't set the ``cmake_file_name`` property, the ``CMakeDeps``
generator would have taken the package name to generate the filename for the config file
and the generated filename would have resulted ``somepkg-config.cmake`` instead of
``some-pkg-config.cmake``.

* Some recipes in Conan Center Index define different ``.names`` values for ``cmake_find_package``
  and ``cmake_find_package_multi``. For these cases, besides ``cmake_target_name`` you should also set
  the ``cmake_module_target_name`` and ``cmake_find_mode`` properties. Let's see an example:

```python
class ExpatConan(ConanFile):
    name = "expat"
    ...
    def package_info(self):
        # creates EXPAT::EXPAT target for module files FindEXPAT.cmake
        self.cpp_info.names["cmake_find_package"] = "EXPAT"
        # creates expat::expat target for config files expat-config.cmake
        self.cpp_info.names["cmake_find_package_multi"] = "expat"
        ...
```

Should translate to the code above. Please note we have added the ``cmake_find_mode``
property for the
[CMakeDeps](https://docs.conan.io/en/latest/reference/conanfile/tools/cmake/cmakedeps.html#properties)
generator with value ``both``.

```python
class ExpatConan(ConanFile):
    name = "expat"
    ...
    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "EXPAT"
        self.cpp_info.names["cmake_find_package_multi"] = "expat"

        # creates EXPAT::EXPAT target for module files FindEXPAT.cmake
        self.cpp_info.set_property("cmake_target_name", "EXPAT::EXPAT")
        # creates expat::expat target for config files expat-config.cmake
        self.cpp_info.set_property("cmake_module_target_name", "expat::expat")

        # generates module file FindEXPAT.cmake
        self.cpp_info.set_property("cmake_file_name", "EXPAT")
        # generates config file expat-config.cmake
        self.cpp_info.set_property("cmake_module_file_name", "expat")

        # config is the default for CMakeDeps
        # we set cmake_find_mode to both to generate both module and config files
        self.cpp_info.set_property("cmake_find_mode", "both")
        ...
```

> *Note**: There are more cases in which you probably want to set the
> ``cmake_find_mode`` property to ``both``. For example, for the libraries which [find
> modules files are included in the CMake
> distribution](https://cmake.org/cmake/help/latest/manual/cmake-modules.7.html#find-modules).

### Translating .filenames information to cmake_file_name, cmake_module_file_name and cmake_find_mode

Like in the ``.names`` case, there are some cases in Conan Center Index of recipes that
set different filenames for ``cmake_find_package`` and ``cmake_find_package_multi``
generators. To translate that information to the ``set_property`` model we have to set the
``cmake_file_name`` and ``cmake_find_mode`` properties. Let's see an example:

```python
class GlewConan(ConanFile):
    name = "glew"
    ...
    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "GLEW"
        self.cpp_info.names["cmake_find_package_multi"] = "GLEW"
        self.cpp_info.filenames["cmake_find_package"] = "GLEW" # generates FindGLEW.cmake
        self.cpp_info.filenames["cmake_find_package_multi"] = "glew" # generates glew-config.cmake
        ...
```

In this case we have to set the ``cmake_find_mode`` property for the
[CMakeDeps](https://docs.conan.io/en/latest/reference/conanfile/tools/cmake/cmakedeps.html#properties)
generator with value ``both``. That will make CMakeDeps generator create both module and
config files for consumers (by default it generates just config files).

```python
class GlewConan(ConanFile):
    name = "glew"
    ...
    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "GLEW"
        self.cpp_info.names["cmake_find_package_multi"] = "GLEW"
        self.cpp_info.filenames["cmake_find_package"] = "GLEW"
        self.cpp_info.filenames["cmake_find_package_multi"] = "glew"

        self.cpp_info.set_property("cmake_target_name", "GLEW::GLEW")

        self.cpp_info.set_property("cmake_file_name", "GLEW") # generates FindGLEW.cmake
        self.cpp_info.set_property("cmake_module_file_name", "glew") # generates glew-config.cmake

        # generate both modules and config files
        self.cpp_info.set_property("cmake_find_mode", "both")
        ...
```

### Understanding some workarounds with the .names attribute model in recipes

The ``.names`` model has some limitations. Because of this, there are some recurrent
workarounds in recipes to achieve things like setting absolute names for targets (without
the ``::`` namespace), or for setting a custom namespace. These workarounds can now be
undone with the ``set_property`` model because it allows setting arbitrary names for CMake
targets. Let's see some examples of these workarounds in recipes:

* **Use of components to get arbitrary target names in recipes**. Some recipes add a component
  whose only role is to get a target name that is not limited by the namespaces added by
  the current generators automatically. For example, the [ktx
  recipe](https://github.com/conan-io/conan-center-index/blob/5753f954027d9d04b6d05e326f2757ab6b1ac69c/recipes/ktx/all/conanfile.py)
  uses this workaround to get a target with name ``KTX::ktx``.

```python
class KtxConan(ConanFile):
    name = "ktx"
    ...

    def package_info(self):
        # changes namespace to KTX::
        self.cpp_info.names["cmake_find_package"] = "KTX"
        ...
        # the target inherits the KTX:: namespace and sets the target KTX::ktx
        self.cpp_info.components["libktx"].names["cmake_find_package"] = "ktx"
        ...
        # all the information is set via this "fake root" component
        self.cpp_info.components["libktx"].libs = ["ktx"]
        self.cpp_info.components["libktx"].defines = [
            "KTX_FEATURE_KTX1", "KTX_FEATURE_KTX2", "KTX_FEATURE_WRITE"
        ]
        ...
```

In these cases, the recommendation is to add the ``cmake_target_name`` property for both
the root and component ``cpp_info``. In the end the target that the consumer will get is
the one created for the component, but it will avoid creating an "unwanted" target if we
add the property just to the component or to the root ``cpp_info``. Please note that when
the migration to Conan 2.0 is done, there will be no need for that component anymore and
it should dissapear. At that moment, the information from the component will be set in the
root ``cpp_info`` and the ``self.cpp_info.components[]`` lines removed.

```python
class KtxConan(ConanFile):
    name = "ktx"
    ...

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "KTX"
        ...
        # FIXME: Remove the libktx component in Conan 2.0, this is just needed for
        # compatibility with current generators
        self.cpp_info.components["libktx"].names["cmake_find_package"] = "ktx"
        ...
        self.cpp_info.components["libktx"].libs = ["ktx"]
        self.cpp_info.components["libktx"].defines = [
            "KTX_FEATURE_KTX1", "KTX_FEATURE_KTX2", "KTX_FEATURE_WRITE"
        ]

        # Set the root cpp_info target name as KTX::ktx for the root and the component
        # In Conan 2.0 the component should be removed
        # and those properties should be added to the root cpp_info instead
        self.cpp_info.set_property("cmake_target_name", "KTX::ktx")
        self.cpp_info.components["libktx"].set_property("cmake_target_name", "KTX::ktx")
        ...
```

* **Use build modules to create aliases with arbitray names for targets**. Similar to the
  previous example, some recipes use a build module with an alias to set an arbitrary
  target name. Let's see the example of the [tensorflow-lite
  recipe](https://github.com/conan-io/conan-center-index/blob/03b24bf128cbf15d23ed988b8d8ca0c0ba87d307/recipes/tensorflow-lite/all/conanfile.py),
  that uses this workaround to define a ``tensorflow::tensorflowlite`` target.

```python
class TensorflowLiteConan(ConanFile):
    name = "tensorflow-lite"
    ...

    def package_info(self):
        # generate the target tensorflowlite::tensorflowlite
        self.cpp_info.names["cmake_find_package"] = "tensorflowlite"
        self.cpp_info.filenames["cmake_find_package"] = "tensorflowlite"
        # this build module defines an alias tensorflow::tensorflowlite to the tensorflowlite::tensorflowlite generated target
        self.cpp_info.build_modules["cmake_find_package"] = [os.path.join(self._module_subfolder, self._module_file)]
        ...
```

To translate this information to the new model, just check which aliases are defined in the
build modules and define those for the new model. In this case it should be enough with
adding the ``tensorflow::tensorflowlite`` target with ``cmake_target_name`` to the root
cpp_info (besides the ``cmake_file_name``property).

```python
class TensorflowLiteConan(ConanFile):
    name = "tensorflow-lite"
    ...

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "tensorflowlite"
        self.cpp_info.filenames["cmake_find_package"] = "tensorflowlite"
        self.cpp_info.build_modules["cmake_find_package"] = [os.path.join(self._module_subfolder, self._module_file)]

        # set the tensorflowlite::tensorflowlite target name directly for CMakeDeps with no need for aliases
        self.cpp_info.set_property("cmake_target_name", "tensorflow::tensorflowlite")
        self.cpp_info.set_property("cmake_file_name", "tensorflowlite")
        ...
```

### Translating .build_modules to cmake_build_modules

Previously we saw that some recipes use a build module with an alias to set an arbitrary target name.
But sometimes the declared ".build_modules" come from the original package that declares useful CMake functions, variables
etc. We need to use the property `cmake_build_modules` to declare a list of cmake files instead of using `cpp_info.build_modules`:

```python
class PyBind11Conan(ConanFile):
    name = "pybind11"
    ...

    def package_info(self):
        ...
        for generator in ["cmake_find_package", "cmake_find_package_multi"]:
            self.cpp_info.components["main"].build_modules[generator].append(os.path.join("lib", "cmake", "pybind11", "pybind11Common.cmake"))
        ...

```

To translate this information to the new model we declare the `cmake_build_modules` property in the `root cpp_info` object:

```python
class PyBind11Conan(ConanFile):
    name = "pybind11"
    ...

    def package_info(self):
        ...
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "pybind11", "pybind11Common.cmake")])
        ...

```

### PkgConfigDeps

The case of ``PkgConfigDeps`` is much more straight forward than the ``CMakeDeps`` case.
This is because the current
[pkg_config](https://docs.conan.io/en/latest/reference/generators/pkg_config.html)
generator suports the new ``set_property`` model for most of the properties. Then, the current
model can be translated to the new one without having to leave the old attributes in the
recipes. Let's see an example:

```python
class AprConan(ConanFile):
    name = "apr"
    ...
    def package_info(self):
        self.cpp_info.names["pkg_config"] = "apr-1"
    ...
```

In this case, you can remove the ``.names`` attribute and just leave:

```python
class AprConan(ConanFile):
    name = "apr"
    ...
    def package_info(self):
        self.cpp_info.set_property("pkg_config_name",  "apr-1")
    ...
```

For more information about properties supported by ``PkgConfigDeps`` generator, please check the [Conan
documentation](https://docs.conan.io/en/latest/reference/conanfile/tools/gnu/pkgconfigdeps.html#properties).
