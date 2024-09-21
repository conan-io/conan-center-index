# Dependencies

This section outlines all the practices and guidelines for the `requirements()` and `build_requirements()` methods. This includes everything
from handling "vendored" dependencies to what versions should be used.

<!-- toc -->
## Contents

  * [List Dependencies](#list-dependencies)
    * [Optional Requirements](#optional-requirements)
    * [Build Requirements](#build-requirements)
  * [Accessing Dependencies](#accessing-dependencies)
    * [Handling Requirement's Options](#handling-requirements-options)
    * [Verifying Dependency's Version](#verifying-dependencys-version)
    * [Passing Requirement's info to `build()`](#passing-requirements-info-to-build)
    * [Overriding the provided properties from the consumer](#overriding-the-provided-properties-from-the-consumer)
  * [Adherence to Build Service](#adherence-to-build-service)
    * [Version Ranges](#version-ranges)
      * [Adding Version Ranges](#adding-version-ranges)
  * [Handling "internal" dependencies](#handling-internal-dependencies)<!-- endToc -->

## List Dependencies

Since all ConanCenterIndex recipes are to build and/or package projects they are exclusively done in [`conanfile.py`](https://docs.conan.io/1/reference/conanfile.html). This offers a few
ways to add requirements. The most common way is [requirements](https://docs.conan.io/1/reference/conanfile/methods.html#requirements):

```py
    def requirements(self):
        self.requires("fmt/9.1.0")
```

> **Note**: With Conan 2.0, you'll also need to pay attention to new properties like the `transitive_header` attributed which is
> needed when a project include a dependencies header files in its public headers.

When a project supports a range of version of a dependency, it's generally advised to pick the **most recent available in ConanCenter**.
This helps ensure there are fewer conflicts with other, up to-date, recipes that share the same requirement.

### Optional Requirements

Many projects support enabling certain features by adding dependencies. In ConanCenterIndex this is done by adding an option, see
[naming recommendation](conanfile_attributes.md#recommended-names), which should be set to match the upstream project's by default.

```py
class ExampleConan(ConanFile):
    options = {
        "with_zlib": [True, False], # Possible values
    }
    default_options = {
        "with_zlib": True, # Should match upstream's CMakeLists.txt `option(...)`
    }

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
```

If a dependency was added (or removed) with a release, then the `if` condition could check [`self.version`](https://docs.conan.io/1/reference/conanfile/attributes.html#version). Another common case is
`self.settings.os` dependant requirements which need to be added for certain plaforms.

### Build Requirements

In ConanCenter we only assume
[CMake is available](../faqs.md#why-recipes-that-use-build-tools-like-cmake-that-have-packages-in-conan-center-do-not-use-it-as-a-build-require-by-default).
If a project requires any other specific tool, those can be added as well. We like to do this with [build_requirements](https://docs.conan.io/1/reference/conanfile/methods.html#build-requirements):

```py
    def build_requirements(self):
        self.tool_requires("ninja/1.1.0")
```

## Accessing Dependencies

It's fairly common to need to pass information from a dependency to the project. This is the job of the [`generate()`](https://docs.conan.io/1/reference/conanfile/methods.html#generate) method. This
is generally covered by the built-in generators like [`CMakeDeps`](https://docs.conan.io/1/reference/conanfile/tools/cmake/cmakedeps.html)
However the [`self.dependencies`](https://docs.conan.io/1/reference/conanfile/dependencies.html?highlight=generate) are available.

Alternatively, a project may depend on a specific versions or configuration of a dependency. This use case is again covered by the
[`self.dependencies`](https://docs.conan.io/1/reference/conanfile/dependencies.html?highlight=validate) within the
[`validate()`](https://docs.conan.io/1/reference/conanfile/methods.html#validate) method. Additionally it's possible to suggest the option's values while the graph is built through [`configure()`](https://docs.conan.io/1/reference/conanfile/methods.html#configure-config-options)
this is not guaranteed and not a common practice.

### Handling Requirement's Options

Forcing options of dependencies inside a ConanCenter should be avoided, except if it is mandatory for the library to build.
Our general belief is the users input should be the most important; it's unexpected for command line arguments to be over ruled
by specifc recipes.

You need to use the [`validate()`](https://docs.conan.io/1/reference/conanfile/methods.html#validate) method in order to ensure they check after the Conan graph is completely built.

Certain projects are dependent on the configuration (also known as options) of a dependency. This can be enforced in a recipe by
accessing the [`options`](https://docs.conan.io/1/reference/conanfile/dependencies.html?highlight=options) field of
the dependency.

```py
  def configure(self):
      self.options["foobar"].enable_feature = True # This will still allow users to override this option

  def validate(self):
      if not self.dependencies["foobar"].options.enable_feature:
          raise ConanInvalidConfiguration(f"{self.ref} requires foobar/*:enable_feature=True.")
```

### Verifying Dependency's Version

Some project requirements need to respect a version constraint, this can be done as follows:

```py
def validate(self):
    if Version(self.dependencies["foobar"].ref.version) < "1.2":
        raise ConanInvalidConfiguration(f"{self.ref} requires [foobar>=1.2] to build and work.")
```

### Passing Requirement's info to `build()`

The [`self.dependencies`](https://docs.conan.io/1/reference/conanfile/dependencies.html) are limited to [`generate()`](https://docs.conan.io/1/reference/conanfile/methods.html#generate) and [`validate()`](https://docs.conan.io/1/reference/conanfile/methods.html#validate). This means configuring a projects build scripts
is a touch more complicated when working with unsupported build scripts.

In general, with [CMake](https://cmake.org/) project, this can be very simple with the [`CMakeToolchain`](https://docs.conan.io/1/reference/conanfile/tools/cmake/cmaketoolchain.html), such as:

```py
    def generate(self):
        tc = CMakeToolchain(self)
        # deps_cpp_info, deps_env_info and deps_user_info are no longer used
        if self.dependencies["dependency"].options.foobar:
            tc.variables["DEPENDENCY_LIBPATH"] = self.dependencies["dependency"].cpp_info.libdirs
```

This pattern can be recreated for less common build system by, generating a script to call configure or capture the
required values in a YAML files for example.

> **Note**: This needs to be saved to disk because the [`conan install`](https://docs.conan.io/1/reference/commands/consumer/install.html) and [`conan build`](https://docs.conan.io/1/reference/commands/development/build.html) commands can be separated when
> developing packages so for this reason the `class` may not persists the information. This is a very common workflow,
> even used in ConanCenter in other areas such as testing.

```py
from conan import ConanFile
from conan.tools.files import save, load


class ExampleConan(ConanFile):
    _optional_build_args = []

    @property
    def _optional_build_args_filename(self):
        return os.path.join(self.recipe_folder, self.folders.generators, "build_args.yml")

    def generate(self):
        # This is required as `self.dependencies` is not available in `build()` or `test()`
        if self.dependencies["foobar"].options.with_compression:
            self._optional_build_args.append("--enable-foobar-compression")

        save(self, self._optional_build_args_filename, file)

    def build(self):
        opts_args = load(self, self._optional_build_args_filename)
        # Some magic setup
        self.run(f"./configure.sh {opts_args}")
```

### Overriding the provided properties from the consumer

> **Note**: This was adding in [Conan 1.55](https://github.com/conan-io/conan/pull/12609) to the generators... we need to
> write docs for when that's available

## Adherence to Build Service

It's very rare we layout "rules", most often it's guidelines, however in order to ensure graph and the package generated are usable
for consumer, we do impose some limits on Conan features to provide a smoother first taste to using Conan.

> **Note**: These are very specific to the ConanCenter being the default remote and may not be relevant to your specifc use case.

* [Version ranges](https://docs.conan.io/1/versioning/version_ranges.html) are generally not allowed (see below for exemption).
* Specify explicit [RREV](https://docs.conan.io/1/versioning/revisions.html) (recipe revision) of dependencies is not allowed.
* Only ConanCenter recipes are allowed in `requires`/`requirements()` and `build_requires`/`build_requirements()`.
* [`python_requires`](https://docs.conan.io/1/reference/conanfile/other.html#python-requires) are not allowed.

### Version Ranges

Version ranges are a useful Conan feature, [documentation here](https://docs.conan.io/2/tutorial/versioning/version_ranges.html).
With the introduction of Conan 2.0, we are currently working to allow the use of version ranges and are allowing this for a handful of dependencies.

Version ranges are being progressively introduced by Conan team maintainers and are being rolled out in phases, and we do not intend
to do it all at once.

Version ranges for the following dependencies will be accepted in pull requests:

* OpenSSL: `[>=1.1 <4]` for libraries known to be compatible with OpenSSL 1.x and 3.x
* CMake: `[>3.XX <4]`, where `3.XX` is the minimum version of CMake required by the relevant build scripts. Note that CCI recipes assume 3.15 is installed in the system, so add this
version range only when a requirement for a newer version is needed.
* Libcurl: `[>=7.78 <9]`
* Zlib: `[>=1.2.11 <2]`
* Libpng: `[>=1.6 <2]`
* Expat: `[>=2.6.2 <3]`
* Libxml2: `[>=2.12.5 <3]`
* Libuv: `[>=1 <2]`
* qt5: `[~5.15]`, if your library depends on qt5, only the 5.15 minor version is allowed
* qt6: `[>=6.x <7]`, where 6.x is the lower bound of your needed qt6 version
* c-ares: `[>=1.27 <2]`
* zstd: `[~1.5]` it's equivalent to `[>=1.5 <1.6]`
* ninja: `[>=1.10.2 <2]`
* meson: `[>=1.2.3 <2]`
* pkgconf: `[>=2.2 <3]`
* xz_utils: `[>=5.4.5 <6]`

> **Warning**: With Conan 1.x, [version ranges](https://docs.conan.io/1/versioning/version_ranges.html) adhere to a much more strict sematic version spec,
> OpenSSL 1.1.x does not follow this so the client will not resolve to that range and will pick a 3.x version. In order to select a lower version you
> can user the defunct `--require-override openssl/1.1.1t@` from the command line, or override from the recipe with `self.requires(openssl/1.1.1t, override=True)`
> to ensure a lower version is picked.

Conan maintainers may introduce this for other dependencies over time. Outside of the cases outlined above, version ranges are not allowed in ConanCenter recipes.

#### Adding Version Ranges

You might also see version ranges being added in pull requests by Conan maintainers, that
are not in the list above. These are being introduced on a case-by-case basis, and are being rolled out
in phases to ensure that they do not cause problems to users. Note that version ranges can
only be used for libraries and tools that have strong compatibility guarantees - and may not
be suitable in all cases.

Please do not open PRs that exclusively add version ranges to dependencies, unless they are solving
current conflicts, in which case we welcome them and they will be prioritized.

## Handling "internal" dependencies

Vendoring in library source code should be removed (in a best effort basis) to avoid potential ODR violations.
If upstream takes care to rename symbols, it may be acceptable.
