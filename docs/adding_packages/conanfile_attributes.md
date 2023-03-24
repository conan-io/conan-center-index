# `ConanFile` Attributes

The `ConanFile` class has a lot of different properties that can help consumers search for projects, help the client build packages for different configurations
or are known by ConanCenter's build service and have special meaning.

<!-- toc -->
## Contents

  * [Attributes](#attributes)
    * [Name](#name)
    * [Version](#version)
      * [ConanCenter specific releases format](#conancenter-specific-releases-format)
    * [License Attribute](#license-attribute)
  * [Order of methods and attributes](#order-of-methods-and-attributes)
  * [Settings](#settings)
  * [Options](#options)
    * [Recommended Names](#recommended-names)
    * [Predefined Options and Known Defaults](#predefined-options-and-known-defaults)
    * [Options to Avoid](#options-to-avoid)<!-- endToc -->

## Attributes

These are a [key feature](https://docs.conan.io/1/reference/conanfile/attributes.html) which allow the Conan client to understand,
identify, and expose recipes and which project they expose.

In ConanCenter, there are a few conventions that need to be respected to ensure recipes can be discovered there `conan search` command
of through the web UI. Many of which are enforces with the [hooks](../error_knowledge_base.md).

### Name

Same as the _recipe folder_ and always lowercase.

Please see the FAQs for:

* [name collisions](../faqs.md#what-is-the-policy-on-recipe-name-collisions)
* [space and symbols](../faqs.md#should-reference-names-use---or-_)

### Version

ConanCenter is geared towards quickly added new release, the build service always pass the version it is currently building to the recipe.
The `version` attribute MUST NOT be added to any recipe - with exception to "system packages".

#### ConanCenter specific releases format

The notation shown below is used for publishing packages which do not match the original library's official releases. This format which includes the "datestamp" corresponding to the date of a commit: `cci.<YEAR MONTH DAY>`.

In order to create reproducible builds, we also "commit-lock" to the latest commit on that day. Otherwise, users would get inconsistent results over time when rebuilding the package. An example of this is the [RapidJSON](https://github.com/Tencent/rapidjson) library, where its package reference is `rapidjson/cci.20200410` and its sources are locked the latest commit on that date in [config.yml](https://github.com/conan-io/conan-center-index/blob/master/recipes/rapidjson/config.yml#L4). The prefix `cci.` is mandatory to distinguish as a virtual version provided by CCI. If you are interested to know about the origin, please, read [here](https://github.com/conan-io/conan-center-index/pull/1464).

### License Attribute

The mandatory license attribute of each recipe **should** be a [SPDX license](https://spdx.org/licenses/) [short Identifiers](https://spdx.dev/ids/) when applicable.

Where the SPDX guidelines do not apply, packages should do the following:

* When no license is provided or it's under the ["public domain"](https://fairuse.stanford.edu/overview/public-domain/welcome/) - these are not a license by itself. Thus, we have [equivalent licenses](https://en.wikipedia.org/wiki/Public-domain-equivalent_license) that should be used instead. If a project falls under these criteria it should be identified as the [Unlicense](https://spdx.org/licenses/Unlicense) license.
* When a custom (e.g. project specific) license is given, the value should be set to `LicenseRef-` as a prefix, followed by the name of the file which contains the custom license. See [this example](https://github.com/conan-io/conan-center-index/blob/e604534bbe0ef56bdb1f8513b83404eff02aebc8/recipes/fft/all/conanfile.py#L8). For more details, [read this conversation](https://github.com/conan-io/conan-center-index/pull/4928/files#r596216206).


## Order of methods and attributes

Prefer the following order of documented methods in python code (`conanfile.py`, `test_package/conanfile.py`):

For `conan create` the order is listed [here](https://docs.conan.io/1/reference/commands/creator/create.html#methods-execution-order)
test packages recipes should append the following methods:

* deploy
* test

the order above resembles the execution order of methods on CI. therefore, for instance, `build` is always executed before `package` method, so `build` should appear before the
`package` in `conanfile.py`.

## Settings

As a general rule, recipes should set the `settings` attribute to: `os`, `arch`, `compiler` and `build_type`, and let Conan compute the package ID based on the settings. Some exceptions apply, as detailed below. For cases not covered here, please reach out to the Conan Center maintainers team for assistance. The following list is not exhaustive:

* **Recipes for _header only_ libraries** or where the contents of the package are the same irrespective of settings, might omit the `settings` attribute altogether, unless there is any logic conditional on a setting value. If the recipe has options or dependencies, but the contents of the package are invariant irrespective of their values, the following logic must be added to ensure a single, unique package ID:

   ```python
   def package_id(self):
      self.info.clear()
   ```

* **Recipes that primarily provide _compiled_ applications** (e.g. `b2`, `cmake`, `make`, ...), which typically applies to packages that are consumed as _tool requires_) must list all
   the settings as well, as they are required during package creation. However, it is advised that the `compiler` setting is removed one in the `package_id()` method as follows:

   ```python
   def package_id(self):
      del self.info.settings.compiler
   ```

   This reflects those cases where tools are consumed exclusively as executables, irrespective of how they were built. Additionally, this reduces the number of configurations generated by CI.

   > **Note** We do not recommend removing the `build_type` setting on these packages, in order to preserve the ability of consumers to run debug executables should they wish to do so.

## Options

Recipes can list any number of options with any meaning, and defaults are up to the recipe itself. The CI cannot enforce anything
in this direction. However, there are a couple of options that have a special meaning for the CI.

### Recommended Names

Adding options is often needed to toggle specific library features on/off. Regardless of the default, there is a strong preference for using positive naming for options. In order to avoid the fragmentation, we recommend using the following naming conventions for such options:

* enable_<feature> / disable_<feature>
* with_<dependency> / without_<dependency>
* use_<feature>

The actual recipe code then may look like:

```py
    options = {"enable_locales": [True, False]} # Changes which files are compiled in to the library
    default_options = {"enable_locales": True}
```

```py
    options = {"with_zlib": [True, False]} # Will add a `self.requires` with more deps to link against
    default_options = {"with_zlib": True}
```

```py
    options = {"use_tzdb": [True, False]} # Might install more headers to expose more features
    default_options = {"use_tzdb": True}
```

Having the same naming conventions for the options helps consumers. It allows users to specify options with wildcards: `-o *:with_threads=True`. Therefore, the `with_threads` options will be enabled for all packages in the graph that support it.

### Predefined Options and Known Defaults

ConanCenter supports many combinations, these are outline in the [supported configurations](../supported_platforms_and_configurations.md) document for each platform.
By default recipes should use `shared=False` with `fPIC=True`. If support, `header_only=False` is the default.

Usage of each option should follow the rules:

* `shared` (with values `True` or `False`). The CI inspects the recipe looking for this option. The **default should be `shared=False`** and will
   generate all the configurations with values `shared=True` and `shared=False`.

   > **Note**: The CI applies `shared=True` only to the package being built, while every other requirement will `shared=False`. To consume everything as a shared library you will set `--build=always` and/or `-o *:shared=True`)
   > It's important to keep this in mind when trying to consume shared packages from ConanCenter
   > as their requirements were linked inside the shared library. See [FAQs](../faqs.md#how-to-consume-a-graph-of-shared-libraries) for more information.

* `fPIC` (with values `True` or `False`). The **default should be `fPIC=True`** and will generate all the configurations with values `fPIC=True` and `fPIC=False`.
  This option does not make sense on all the support configurations so it should be removed.

   ```python
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

   def configure(self):
      if self.options.shared:
         self.options.rm_safe("fPIC")
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
   Instead, use Conan config [skip_test](https://docs.conan.io/1/reference/config_files/global_conf.html#tools-configurations) feature:

   ```python
   def generate(self):
      tc = CMakeToolChain(self)
      tc.variables['BUILD_TESTING'] = not self.conf.get("tools.build:skip_test", default=true, check_type=bool)
   ```

   The `skip_test` configuration is supported by [CMake](https://docs.conan.io/1/reference/build_helpers/cmake.html#test) and [Meson](https://docs.conan.io/1/reference/build_helpers/meson.html#test).

 ### Removing from `package_id`

 By default, options are included in the calculation for the `package_id` ([docs](https://docs.conan.io/1/reference/conanfile/methods.html#package-id)).
 Options which do not impact the generated packages should be deleted, for instance adding a `#define` for a package.

 ```python
def package_id(self):
   del self.info.options.enable_feature

def package_info(self):
   if self.options.enable_feature:
      self.cpp_info.defines.append("FOBAR_FEATURE=1")
```
