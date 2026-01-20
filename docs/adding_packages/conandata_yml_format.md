# conandata.yml

[conandata.yml](https://docs.conan.io/2/tutorial/creating_packages/handle_sources_in_packages.html#using-the-conandata-yml-file) is a [YAML](https://yaml.org/)
file to provide declarative data for the recipe (which is imperative). This is a built-in Conan feature (available since
1.22.0) without a fixed structure, but ConanCenter has a specific format to ensure quality of recipes.

In the context of ConanCenterIndex, this file is _mandatory_ and consists of two main sections that will be explained in the
next sections with more detail:

* `sources`: Library sources origin with their verification checksums.
* `patches`: A list of patches to apply and supporting information. See the [Patching Policy](sources_and_patches.md#policy-about-patching) for the criteria.

<!-- toc -->
## Contents

  * [sources](#sources)
    * [Mirrors](#mirrors)
    * [Multiple Assets](#multiple-assets)
      * [Different source archives per configuration](#different-source-archives-per-configuration)
    * [Sources fields](#sources-fields)
      * [url](#url)
      * [sha256](#sha256)
  * [patches](#patches)
    * [Patches fields](#patches-fields)
      * [patch_file](#patch_file)
      * [patch_description](#patch_description)

## sources

`sources` is a top level dictionary, containing entries of sources and checksums for each of the supported versions.

This is the entry that contains all the items that are downloaded from the internet and used in a recipe. This section contains one entry per version and each version should declare its own sources.

> **Note**: For deciding which source to pick, see [Picking Sources](sources_and_patches.md#picking-the-sources) guide.

This is a basic example of a regular library, it should satisfy most of the use cases:

```yml
sources:
   "1.2.11":
       url: "..."
       sha256: "..."
   "1.2.12":
       url: "..."
       sha256: "..."
```

Every entry for a version consists in a dictionary with the `url` and the hashing algorithm of the artifact. `sha256` is required, but others like `sha1` or `md5` can be used as well.

### Mirrors

Sometimes it is useful to declare mirrors, use a list in the `url` field. Conan will try to download the artifacts from any of those mirrors.

```yml
sources:
  "1.2.11":
    url:
    - "https://zlib.net/zlib-1.2.11.tar.gz",
    - "https://downloads.sourceforge.net/project/libpng/zlib/1.2.11/zlib-1.2.11.tar.gz",
    sha256: "c3e5e9fdd5004dcb542feda5ee4f0ff0744628baf8ed2dd5d66f8ca1197cb1a1"
```

Keep in mind all the mirrors have to provide the exactly same source (e.g. no repackaging), thus using the same hash sum.

### Multiple Assets

It's rare but some projects ship archives missing files that are required to build or specifically to ConanCenter requirements.
You can name each asset and download them in the `conanfile.py`'s `source()` referring to the names.

```yml
sources:
  "10.12.2":
    "sources":
      url: https://github.com/approvals/ApprovalTests.cpp/releases/download/v.10.12.2/ApprovalTests.v.10.12.2.hpp
      sha256: 4c43d0ea98669e3d6fbb5810cc47b19adaf88cabb1421b488aa306b08c434131
    "license":
      url: "https://raw.githubusercontent.com/approvals/ApprovalTests.cpp/v.10.12.2/LICENSE"
      sha256: c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4
```

You can list as many assets you need and reference them by their index. But make sure you keep them in order if there is any specific
logic about handling.

```yml
sources:
  "10.12.2":
    - url: https://github.com/approvals/ApprovalTests.cpp/releases/download/v.10.12.2/ApprovalTests.v.10.12.2.hpp
      sha256: 4c43d0ea98669e3d6fbb5810cc47b19adaf88cabb1421b488aa306b08c434131
    - url: "https://raw.githubusercontent.com/approvals/ApprovalTests.cpp/v.10.12.2/LICENSE"
      sha256: c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4
```

#### Different source archives per configuration

This is the most advanced and sophisticated use-case, but not so common. Some projects may provide different sources for different platforms, it could be expressed as:

```yml
sources:
  "0066":
    "Macos": # Operating system
      "x86": # Architecture
      - url: "https://naif.jpl.nasa.gov/pub/naif/misc/toolkit_N0066/C/MacIntel_OSX_AppleC_32bit/packages/cspice.tar.Z"
        sha256: "9a4b5f674ea76821c43aa9140829da4091de646ef3ce40fd5be1d09d7c37b6b3"
      "x86_64":
      - url: "https://naif.jpl.nasa.gov/pub/naif/misc/toolkit_N0066/C/MacIntel_OSX_AppleC_64bit/packages/cspice.tar.Z"
        sha256: "f5d48c4b0d558c5d71e8bf6fcdf135b0943210c1ff91f8191dfc447419a6b12e"
```

This approach requires a special code within [build](https://docs.conan.io/2/reference/conanfile/methods/build.html) method to handle.

### Sources fields

#### url

`url` contains a string specifying [URI](https://tools.ietf.org/html/rfc3986) where to download released sources.
Usually, `url` has a [https](https://tools.ietf.org/html/rfc2660) scheme, but other schemes, such as [ftp](https://tools.ietf.org/html/rfc959) are accepted as well.

#### sha256

[sha256](https://tools.ietf.org/html/rfc6234) is a preferred method to specify hash sum for the released sources. It allows to check the integrity of sources downloaded.
You may use an [online service](https://hash.online-convert.com/sha256-generator) to compute `sha256` sum for the given file located at `url`.

If you're using linux you can run `wget -q -O - url | sha256sum` to get the hash which uses the [sha256sum](https://linux.die.net/man/1/sha256sum) command ([windows](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-filehash?view=powershell-7.4) you can use PowerShell).

## patches

Sometimes sources provided by project require patching for various reasons. The `conandata.yml` file is the right place to indicate this information as well.

> **Note**: All patches introduced in PR will be merged under strict review by maintainers. 
> Before adding a patch, **make sure to read** our [Policy on Patches](sources_and_patches.md#policy-about-patching)

This section follows the same pattern as the `sources` above - one entry per version with a list of patches to apply.

```yaml
patches:
  "1.2.0":
    - patch_file: "patches/1.2.0-002-link-core-with-find-library.patch"
      patch_description: "Link CoreFoundation and CoreServices with find_library"
```

### Patches fields

Only the `patch_file` field is required for the recipe to work properly.
Additional information to motivate and justify the patch should be provided in the PR that introduces is. Optionally, consider adding a more thorough description as described below if deemed necessary.

#### patch_file

_Required_

Patch file that are committed to the ConanCenterIndex, go into the `patches` sub-directory (next to the `conanfile.py`). Such patch files usually have either `.diff` or `.patch` extension. The recommended way to generate such patches is [git format-patch](https://git-scm.com/docs/git-format-patch). The path to the patch is relative to the directory containing `conandata.yml` and `conanfile.py`.

#### patch_description

_Optional_

`patch_description` is an arbitrary text describing what the patch does.

This is optional. Please **only** use it if the description adds relevant information that is not already present in the `patch_file` name.


✅
Example:
```
    - patch_file: "patches/8.9.0-0001-cve-2023-50980.patch"
      patch_description: "Validate PolynomialMod2 coefficients (CVE-2023-50980)"
```

❌ Avoid the following, as it doesn't add any new information:
```
    - patch_file: "patches/1.1.2-0001-fix-windows-static.patch"
      patch_description: "Fix windows static"
```

If a patch requires additional information, please:
- Make sure new patches are properly explained and motivated in the PR description
- Consider using the header preamble of the patch for a more thorough description (example [here](https://github.com/conan-io/conan-center-index/blob/52a6bf00682053907708e08a44c514f42bcc7d00/recipes/anyrpc/all/patches/0002-fix-shared-library-1.0.2.patch#L1-L6)) or to add a reference to a pre-existing upstream patch (example [here](https://github.com/conan-io/conan-center-index/blob/52a6bf00682053907708e08a44c514f42bcc7d00/recipes/civetweb/all/patches/0002-1.14-fix-option-handling.patch#L1-L8)).