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

These are a [key feature](https://docs.conan.io/2/reference/conanfile/attributes.html) which allows the Conan client to understand,
identify, and expose recipes and which project they expose.

In ConanCenter, there are a few conventions that need to be respected to ensure recipes can be discovered there `conan search` command
of through the web UI.

### Name

Same as the _recipe folder_ and always lowercase.

Please see the FAQs for:

* [name collisions](../faqs.md#what-is-the-policy-on-recipe-name-collisions)
* [naming forks](../faqs.md##what-is-the-policy-for-naming-forks)
* [space and symbols](../faqs.md#should-reference-names-use---or-_)

### Version

The `version` attribute MUST NOT be added to any recipe - with exception to "system packages".

#### ConanCenter specific releases format

The notation shown below is used for publishing packages which do not match the original library's official releases.

There are two cases to consider:

* The library has not had any previous releases/tags. In this case, the version should be of the form
  `0.0.0.cci.<YEAR MONTH DAY>`. For example, `0.0.0.cci.20240402`. When/if a version of the library is ever released.
  this will allow version ranges to properly identify the release as a newer version.
* The library has had previous releases/tags. In this case, the version should be of the form
  `<MAJOR>.<MINOR>.<PATCH>.cci.<YEAR MONTH DAY>`. For example, `1.2.0.cci.20240402`.
  This will allow version ranges to properly identify the release as a newer version.

In order to create reproducible builds, we also "commit-lock" to the latest commit on that day, so the sources should point
to the commit hash of that day. Otherwise, users would get inconsistent results over time when rebuilding the package.

### License Attribute

The license attribute is a mandatory field which provides the legal information that summarizes the contents saved in the package. These follow the
[SPDX license](https://spdx.org/licenses/) as a standard. This is for consumers, in particular in the enterprise sector, that do rely on SDPX compliant identifiers so that they can flag this as a custom license text.

* If the library has a license that has a SPDX identifier, use the [short Identifiers](https://spdx.dev/ids/).
* If the library has a license text that does not match a SPDX identifier, including custom wording disclaiming copyright or dedicating the words to the ["public domain"](https://fairuse.stanford.edu/overview/public-domain/welcome/), use the [SPDX License Expressions](https://spdx.github.io/spdx-spec/v2-draft/SPDX-license-expressions/), this can follow:
  * `LicenseRef-` as a prefix, followed by the name of the library. For example:`LicenseRef-libfoo-public-domain`
  * If the license is extracted from a specific document, prepend `DocumentRef-<filename>-` to the license name. For example: `DocumentRef-README.md-LicenseRef-libfoo-public-domain`
* If the library makes no mention of a license and the terms of use - it **shall not be accepted in ConanCenter** , even if the code is publicly available in GitHub or any other platforms.

In case the license changes in a new release, the recipe should update the license attribute accordingly:

```python
class LibfooConan(ConanFile):
    license = "MIT"

    def configure (self):
       # INFO: Version < 2.0 the license was MIT, but changed to BSD-3-Clause now.
       if Version(self.version) >= "2.0.0":
          self.license = "BSD-3-Clause"
```

## Order of methods and attributes

Prefer the following order of documented methods in python code (`conanfile.py`, `test_package/conanfile.py`):

For `conan create` the order is listed [here](https://docs.conan.io/2/reference/commands/create.html#methods-execution-order).

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

By default recipes should use `*/*:shared=False` with `*/*:fPIC=True`. If supported, `&:header_only=False` is the default.

Usage of each option should follow the rules:

* `shared` (with values `True` or `False`). The CI inspects the recipe looking for this option. The **default should be `shared=False`** and will
   generate all the configurations with values `shared=True` and `shared=False`.

* `fPIC` (with values `True` or `False`). The **default should be `fPIC=True`** and will generate all the configurations with values `fPIC=True` and `fPIC=False`.
  This option does not make sense on all the support configurations, so using `implements` is recommended:

   ```python
   implements = ["auto_shared_fpic"]
   ```

* `header_only` (with values `True` or `False`). The **default should be `header_only=False`**. If the CI detects this option, it will generate all the
   configurations for the value `header_only=False` and add one more configuration with `header_only=True`. **Only one package**
   will be generated for `header_only=True`, so it is crucial that the package is actually a _header only_ library, with header files only (no libraries or executables inside).

   Recipes with such options should include the following in their `implements` attribute:

   ```python
   implements = ["auto_header_only"]
   ```

### Options to Avoid

* `build_testing` should not be added, nor any other related unit test option. Options affect the package ID, therefore, testing should not be part of that.
   Instead, use Conan config [skip_test](https://docs.conan.io/2/reference/config_files/global_conf.html#user-tools-configurations) feature.

   The `skip_test` configuration is supported by [CMake](https://docs.conan.io/2/reference/tools/cmake/cmake.html) and [Meson](https://docs.conan.io/2/reference/tools/meson/meson.html).

 ### Removing from `package_id`

 By default, options are included in the calculation for the `package_id` ([docs](https://docs.conan.io/2/reference/binary_model/package_id.html)).
 Options which do not impact the generated packages should be deleted, for instance adding a `#define` for a package.

 ```python
def package_id(self):
   del self.info.options.enable_feature

def package_info(self):
   if self.options.enable_feature:
      self.cpp_info.defines.append("FOBAR_FEATURE=1")
```
