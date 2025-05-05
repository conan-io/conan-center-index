# Sources and Patches

This documents contains everything related to the `source()`. This includes picking sources, where they should come from and goes into when and how to modify sources.
These are a very important aspects and it helps us to establish the quality of the packages offered by ConanCenter.

<!-- toc -->
## Contents

  * [Picking the Sources](#picking-the-sources)
    * [Source immutability](#source-immutability)
    * [Sources not accessible](#sources-not-accessible)
  * [Supported Versions](#supported-versions)
    * [Removing old versions](#removing-old-versions)
    * [Adding old versions](#adding-old-versions)
  * [Policy about patching](#policy-about-patching)
    * [Format and Conventions](#format-and-conventions)
    * [Exporting Patches](#exporting-patches)
    * [Applying Patches](#applying-patches)
    * [Policy on patches](#policy-on-patches)<!-- endToc -->

## Picking the Sources

This is one of the most important steps when contributing and the quality of the sources directly dictates the quality of the packages produced.
The **origin of sources** should come from an official origin like the library source code repository or the official
release/download webpage. If an official source archive is available, it should be preferred over an auto-generated archive.

Recipes should always be **built from library sources**. It aims to provide packages that respect the complete setting model of Conan.
Where ever possible, downloading source files and compiling is mandated. Downloading pre-compiled binaries should be avoided.

### Source immutability

Downloaded source code must have a deterministic results where the exact same archive is download each time. See
[Conandata's `"sha"` fields](conandata_yml_format.md#sha256) for how this is achieved in ConanCenterIndex.

The sources stored under `self.source_folder` should not be modified. This will enable local workflows to "keep sources" and avoid extra downloads.
Any patch should be applied to the copy of this source code when a build is executed (basically in `build()` method). See [Applying Patches](#applying-patches)
below for more information.

### Sources not accessible

Library sources that are not publicly available will not be allowed in this repository even if the license allows their redistribution. See
our [closed source FAQ answer for more](../faqs.md#how-to-package-libraries-that-depend-on-proprietary-closed-source-libraries).
If library sources cannot be downloaded from their official origin or cannot be consumed directly due to their
format, the recommendation is to contact the publisher and ask them to provide the sources in a way/format that can be consumed
programmatically.

As a final option, in case you need to use those binaries as a "build require" for some library, we will consider adding it
as a system recipe (`<build_require>/system`) and making those binaries available in the CI machines (if the license allows it).

## Supported Versions

In this repository we are building a subset of all the versions for a given library. This set of version changes over time as new versions
are released and old ones stop being used.

We always welcome latest releases as soon as they are available, and from time to time we remove old versions mainly due to technical reasons:
the more versions we have, the more resources that are needed in the CI and the more time it takes to build each pull-request (also, the
more chances of failing because of unexpected errors).

### Removing old versions

The Conan Team may ask you to remove more if they are taking a lot of resources. When removing old versions, please follow these considerations:

* keep one version for every major release
* for the latest major release, at least three versions should be available (latest three minor versions)

Logic associated with removed revisions implies that entries in the `config.yml` and `conandata.yml` files should also be removed. If anyone needs to
recover them in the future, Git contains the full history and changes can be recovered from it.

Please, note that even if those versions are removed from this repository, **the packages will always be accessible in ConanCenter remote**
associated to the recipe revision used to build them.

### Adding old versions

We love to hear why in the opening description of the pull requests you need this exact version.
We usually don't add old versions unless there is a specific request for it. Adding versions that are not used by author of the pull request reduces overall resources and time from [the build services](README.md#the-build-service).

Take into account that the version might be removed in future pull requests according to the [guidelines above](#removing-old-versions).

## Policy about patching

The main guideline in ConanCenter is to provide already compiled binaries for a set of architectures in the least surprising way as possible, so Conan
can be plugged into existing projects trying to minimize the modifications needed. Packages from Conan Center should fulfill the expectations of anyone
reading the changelog of the library, the documentation, or any statement by the library maintainers.

### Format and Conventions

Patch files are preferred over programmatic `replace_in_file` statements. This makes it easier to review and prevent
unwanted side effects when new versions are added. They will be listed in [`conandata.yml`](conandata_yml_format.md)
file and exported together with the recipe. Patches must always include [patch fields](conandata_yml_format.md#patches-fields)
which are enforced by the [linters](../../linter/conandata_yaml_linter.py).

Patches must be located in the recipe folder in a `patches/` sub-directory.

There are a few recommendations about naming patches:

* be descriptive but terse
* number them so they can be re-used
* note the specific version

By clearly indicating what the patch does, when it's applied, and how it relates to existing patches, you can
help make the [review process](../review_process.md) easier for readers and help speed up your pull requests.

### Exporting Patches

It's ideal to minimize the number of files in a package to exactly what's required. When recipes support multiple
versions with differing patches, it's strongly encouraged to only export the patches used for that given recipe.

Make sure the `export_sources` attribute is replaced by
[`conan.tools.files.export_conandata_patches`](https://docs.conan.io/1/reference/conanfile/tools/files/patches.html?highlight=export_conandata_patches)
helper.

```py
def export_sources(self):
    export_conandata_patches(self)
```

### Applying Patches

Patches can be applied in a separate method, the pattern name is `_patch_sources`. When applying patch files,
using [`conan.tools.files.apply_conandata_patches`](https://docs.conan.io/1/reference/conanfile/tools/files/patches.html?highlight=apply_conandata_patches)
is the best option.

```py
def build(self):
    apply_conandata_patches(self)
```

For more complicated cases,
[`conan.tools.files.rm`](https://docs.conan.io/1/reference/conanfile/tools/files/basic.html#conan-tools-files-rm)
or [`conan.tools.files.replace_in_file`](https://docs.conan.io/1/reference/conanfile/tools/files/basic.html#conan-tools-files-replace-in-file)
are good choices.

```py
def _patch_sources(self):
    # remove bundled libfmt
    rmdir(self, os.path.join(self.source_folder, "lib", "fmt"))
    replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "${CMAKE_SOURCE_DIR}", "${CMAKE_CURRENT_SOURCE_DIR}")
```

### Policy on patches

Conan Center is a package repository, and the aim of the service is to provide the recipes to build libraries from the sources as provided by the library authors, and to provide binaries for Conan Center’s supported platforms and configurations.

In general, patches to source code should be avoided and only done as a last resort. In situations where it is strictly necessary, the aim should be that the patches could be eventually merged upstream so that in the future they are no longer necessary. 

Pull Requests that introduce patches will be carefully reviewed by the Conan Team.  We recognize that in some instances, patches are necessary in the build system/build scripts. 
Patches that affect C and C++ code are strongly discouraged and will only be accepted at the discretion of the Conan Team, after a strict validation process. Patches are more likely to be accepted if they are first reported and acknowledged by the library authors.

For scenarios that require patching source code, we greatly encourage raising a new issue explaining the need and motivation, reproducible steps and complete logs, behind the patch. Please note that for issues that strictly affect C and C++ source code, it is very unlikely that a patch will be accepted if an issue is not first raised with the original library authors, or if the patches are not addressing a known security advisory.
