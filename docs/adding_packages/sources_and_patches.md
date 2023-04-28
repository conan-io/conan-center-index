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
    * [Rules](#rules)
    * [Exceptions](#exceptions)<!-- endToc -->

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

### Rules

These are the rules that apply to regular versions of Conan packages:

**Build system patches.** In order to add libraries into ConanCenter sometimes
it is NEEDED to apply patches so they can consume existing packages
for requirements and binaries can be generated. These patches are totally
needed for the purpose of ConanCenter and Conan keeps adding features trying
to minimize these changes.

**Source patches.** ConanCenter DOES NOT accept patches **backporting bugfixes or
features** from upcoming releases, they break the principle of minimum surprise,
they change the behavior of the library and it will no longer match the
documentation or the changelog originally delivered by the authors.

However, ConanCenter DOES accept **working software patches**, these patches
are needed to generate the binaries for architectures not considered by
library maintainers, or to use some compilers or configurations. These patches
make it possible to generate binaries that cannot be generated otherwise, or
they can turn a crashing binary into a working software one (bugs, errors, or
faults are considered working software as long as they produce deterministic
results).

Patches to sources to add support to newer versions of dependencies are
considered feature patches and they are not allowed either. They can
introduce new behaviors or bugs not considered when delivering the
library by maintainers. If a requirement is known not to work, the recipe
should raise a `ConanInvalidConfiguration` from the `validate()` method.

**Vulnerability patches.** Patches published to CVE databases or declared as
vulnerabilities by the authors in non-mainstream libraries WILL be applied
to packages generated in Conan Center.

**Official release patches.** If the library documents that a patch should be
applied to sources when building a tag/release from sources, ConanCenter WILL
apply that patch too. This is needed to match the documented behavior or the
binaries of that library offered by other means.
[Example here](https://www.boost.org/users/history/version_1_73_0.html).

### Exceptions

Exceptionally, we might find libraries that aren't actively developed and consumers
might benefit from having some bugfixes applied to previous versions while
waiting for the next release, or because the library is no longer maintained. These
are the rules for this exceptional scenario:

* **new release**, based on some official release and clearly identifiable will
 be created to apply these patches to: <<PLACEHOLDER_FOR_RELEASE_FORMAT>>.
* **only patches backporting bugfixes** will be accepted after they have
 been submitted to the upstream and there is a consensus that it's a bug and the patch is the solution.

ConanCenter will build this patched release and serve its binaries like it does with
any other Conan reference.

Notice that these <<PLACEHOLDER_FOR_RELEASE_FORMAT>> releases are unique to ConanCenter
and they can get new patches or discard existing ones according to upstream
considerations. It means that these releases will modify their behavior without previous
notice, the documentation or changelog for these specific releases won't exist. Use
them carefully in your projects.
