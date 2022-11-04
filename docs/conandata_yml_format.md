# conandata.yml

[conandata.yml](https://docs.conan.io/en/latest/reference/config_files/conandata.yml.html) is a [YAML](https://yaml.org/) file to provide declarative data for the recipe (which is imperative). `conandata.yml` is a built-in Conan feature (available since 1.22.0) without a fixed structure, but ConanCenterIndex uses it for its own purposes and imposes some requirements.

In the context of ConanCenterIndex, this file is mandatory and consists of two main sections that we will explain in the next sections with more detail:

* `sources`: Library sources origin with their verification checksums. Freeform structure specific to a recipe.
* `patches`: Details about the different patches the library needs along with details for traceability.

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
      * [patch_type](#patch_type)
        * [official](#official)
        * [vulnerability](#vulnerability)
        * [backport](#backport)
        * [portability](#portability)
        * [conan](#conan)
      * [patch_source](#patch_source)
      * [base_path](#base_path)
      * [sha256](#sha256-1)<!-- endToc -->

## sources

`sources` is a top level dictionary, containing entries of sources and checksums for each of the supported versions.

This is the entry that contains all the items that are downloaded from the internet and used in a recipe. This section contains one entry per version and each version should declare its own sources.

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

This approach requires a special code within [build](https://docs.conan.io/en/latest/reference/conanfile/methods.html#build) method to handle.

### Sources fields

#### url

`url` contains a string specifying [URI](https://tools.ietf.org/html/rfc3986) where to download released sources.
Usually, `url` has a [https](https://tools.ietf.org/html/rfc2660) scheme, but other schemes, such as [ftp](https://tools.ietf.org/html/rfc959) are accepted as well.

#### sha256

[sha256](https://tools.ietf.org/html/rfc6234) is a preferred method to specify hash sum for the released sources. It allows to check the integrity of sources downloaded.
You may use an [online service](https://hash.online-convert.com/sha256-generator) to compute `sha256` sum for the given `url`.
Also, you may use [sha256sum](https://linux.die.net/man/1/sha256sum) command ([windows](http://www.labtestproject.com/files/win/sha256sum/sha256sum.exe)).

## patches

Sometimes sources provided by project require patching for various reasons. The `conandata.yml` file is the right place to indicate this information as well.

This section follows the same pattern as the `sources` above: one entry per version with a list of patches to apply.

```yaml
patches:
  "1.2.0":
    - patch_file: "patches/1.2.0-002-link-core-with-find-library.patch"
      patch_description: "Link CoreFoundation and CoreServices with find_library"
      patch_type: "portability"
      patch_source: "https://a-url-to-a-pull-request-mail-list-topic-issue-or-question"
```

### Patches fields

Theres are necessary for Conan to work as well as provide key information to reviewers and consumers which need to understand
the reasoning behind patches.

#### patch_file

_Required_

Patch file that are committed to the ConanCenterIndex, go into the `patches` sub-directory (next to the `conanfile.py`). Such patch files usually have either `.diff` or `.patch` extension. The recommended way to generate such patches is [git format-patch](https://git-scm.com/docs/git-format-patch). The path to the patch is relative to the directory containing `conandata.yml` and `conanfile.py`.

#### patch_description

_Required_

`patch_description` is an arbitrary text describing the following aspects of the patch:

* What does patch do (example - `add missing unistd.h header`)
* Why is it necessary (example - `port to Android`)
* How exactly does patch achieve that (example - `update configure.ac`)

An example of a full patch description could be: `port to Android: update configure.ac adding missing unistd.h header`.

#### patch_type

_Required_

The `patch_type` field specifies the type of the patch. In ConanCenterIndex we currently accept only several kind of patches:

##### official

`patch_type: official` indicates the patch is distributed with source code itself. usually, this happens if release managers failed to include a critical fix to the release, but it's too much burden for them to make a new release just because of that single fix.
[example](https://www.boost.org/users/history/version_1_72_0.html) (notice the `coroutine` patch)

##### vulnerability

`patch_type: vulnerability`: Indicates a patch that addresses the security issue. The patch description
should include the index of CVE or CWE the patch addresses.
Usually, original library projects do new releases fixing vulnerabilities for this kind of issues, but in some cases they are either abandoned or inactive.

##### backport

> **Note**: These are likely to undergo extra scrutiny during review as they may modify the source code.

`patch_type: backport`: Indicates a patch that backports an existing bug fix from the newer release or master branch (or equivalent, such as main/develop/trunk/etc). The [`patch_source`](#patch_source) may be a pull request, or bug within the project's issue tracker.
Backports are accepted only for bugs that break normal execution flow, never for feature requests.
Usually, the following kind of problems are good candidates for backports:

* Program doesn't start at all.
* Crash (segmentation fault or access violation).
* Hang up or deadlock.
* Memory leak or resource leak in general.
* Garbage output.
* Abnormal termination without a crash (e.g. just exit code 1 at very beginning of the execution).
* Data corruption.
* Use of outdated or deprecated API or library.

As sources with backports don't act exactly the same as the version officially released, it may be a source of confusion for the consumers who are relying on the buggy behavior (even if it's completely wrong). Therefore, it's required to introduce a new `cci.<YYYYMMDD>` version for such backports, so consumers may choose to use either official version, or modified version with backport(s) included.

##### portability

`patch_type: portability`: Indicates a patch that improves the portability of the library, e.g. adding supports of new architectures (ARM, Sparc, etc.), operating systems (FreeBSD, Android, etc.), compilers (Intel, MinGW, etc.), and other types of configurations which are not originally supported by the project.
In such cases, the patch could be adopted from another package repository (e.g. MSYS packages, Debian packages, Homebrew, FreeBSD ports, etc.).
Patches of this kind are preferred to be submitted upstream to the original project repository first, but it's not always possible.
Some projects simply do not accept patches for platforms they don't have a build/test infrastructure, or maybe they are just either abandoned or inactive.

##### conan

`patch_type: conan`: Indicates a patch that is Conan-specific, patches of such kind are usually not welcomed upstream at all, because they provide zero value outside of Conan.
Examples of such a patches may include modifications of build system files to allow dependencies provided by Conan instead of dependencies provided by projects themselves (e.g. as submodule or just 3rd-party sub-directory) or by the system package manager (rpm/deb).
Such patches may contain variables and targets generated only by Conan, but not generated normally by the build system (e.g. `CONAN_INCLUDE_DIRS`).

#### patch_source

_Optional_

`patch_source` is the URL from where patch was taken from. https scheme is preferred, but other URLs (e.g. git/svn/hg) are also accepted if there is no alternative. Types of patch sources are:

* Link to the public commit in project hosting like GitHub/GitLab/BitBucket/Savanha/SourceForge/etc.
* Link to the Pull Request or equivalent (e.g. gerrit review).
* Link to the bug tracker (such as JIRA, BugZilla, etc.).
* Link to the mail list discussion.
* Link to the patch itself in another repository (e.g. MSYS, Debian, etc.).

For the `patch_type: portability` there might be no patch source matching the definition above. Although we encourage contributors to submit all such portability fixes upstream first, it's not always possible (e.g. for projects no longer maintained). In that case, a link to the Conan issue is a valid patch source (if there is no issue, you may [create](https://github.com/conan-io/conan-center-index/issues/new/choose) one).
For the `patch_type: conan`, it doesn't make sense to submit patch upstream, so there will be no patch source.

#### base_path

_Optional_

Specifies a sub-directory in project's sources to apply patch. This directory is relative to the [source_folder](https://docs.conan.io/en/latest/reference/conanfile/attributes.html?highlight=source_folder#source-folder). Usually, it would be a `source_subfolder`, but could be a lower-level sub-directory (e.g. if it's a patch for a submodule).
