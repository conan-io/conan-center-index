# Dependencies

This section outlines all the practices and guidelines for the `requirements()` and `build_requirements()` methods. This includes everything
from handling "vendored" dependencies to what versions should be used.

<!-- toc -->
## Contents
  * [Handling Requirement's Options](#handling-requirements-options)
  * [Adherence to Build Service](#adherence-to-build-service)
    * [Version Ranges](#version-ranges)
    * [Adding Version Ranges](#adding-version-ranges)
  * [Handling "internal" dependencies](#handling-internal-dependencies)<!-- endToc -->



## Handling Requirement's Options

Forcing options of dependencies inside a ConanCenter should be avoided, except if it is mandatory for the library to build.
Our general belief is the users input should be the most important; it's unexpected for command line arguments to be over ruled
by specifc recipes.

You need to use the [`validate()`](https://docs.conan.io/2/reference/conanfile/methods/validate.html) method in order to ensure they check after the Conan graph is completely built.

Certain projects are dependent on the configuration (also known as options) of a dependency. This can be enforced in a recipe by
accessing the [`options`](https://docs.conan.io/2/reference/conanfile/methods/generate.html#dependencies-interface) field of
the dependency.

```py
  def configure(self):
      self.options["foobar"].enable_feature = True # This will still allow users to override this option

  def validate(self):
      if not self.dependencies["foobar"].options.enable_feature:
          raise ConanInvalidConfiguration(f"{self.ref} requires foobar/*:enable_feature=True.")
```

## Adherence to Build Service

It's very rare we layout "rules", most often it's guidelines, however in order to ensure graph and the package generated are usable
for consumer, we do impose some limits on Conan features to provide a smoother first taste to using Conan.

> **Note**: These are very specific to the ConanCenter being the default remote and may not be relevant to your specifc use case.

* [Version ranges](https://docs.conan.io/2/tutorial/versioning/version_ranges.html#range-expressions) are generally not allowed ([see below](https://github.com/conan-io/conan-center-index/blob/master/docs/adding_packages/dependencies.md#version-ranges) for exemptions).
* Specify explicit [RREV](https://docs.conan.io/2/tutorial/versioning/revisions.html) (recipe revision) of dependencies is not allowed.
* Only ConanCenter recipes are allowed in `requires`/`requirements()` and `build_requires`/`build_requirements()`.
* [`python_requires`](https://docs.conan.io/2/reference/extensions/python_requires.html) are not allowed.

### Version Ranges

Version ranges are a useful Conan feature, [documentation here](https://docs.conan.io/2/tutorial/versioning/version_ranges.html).
With the introduction of Conan 2.0, we are currently working to allow the use of version ranges and are allowing this for a handful of dependencies.

Version ranges are being progressively introduced by Conan team maintainers and are being rolled out in phases, and we do not intend
to do it all at once.

Version ranges for the following dependencies will be accepted in pull requests:

* OpenSSL: `[>=1.1 <4]` for libraries known to be compatible with OpenSSL 1.x and 3.x
* CMake: `[>3.XX <4]`, where `3.XX` is the minimum version of CMake required by the relevant build scripts. Note that CCI recipes assume 3.15 is installed in the system, so add this
version range only when a requirement for a newer version is needed.
* doxygen: `[>=1.8 <2]`
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

Conan maintainers may introduce this for other dependencies over time. Outside of the cases outlined above, version ranges are not allowed in ConanCenter recipes.

### Adding Version Ranges

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
