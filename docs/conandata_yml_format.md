# conandata.yml

[conandata.yml](https://docs.conan.io/en/latest/reference/config_files/conandata.yml.html) is a [YAML](https://yaml.org/) file to provide declarative data for the recipe (which is imperative).

`conandata.yml` is built-in conan feature, but conan-center-index uses it for its own purposes.

## sources

`sources` is a top level dictionary, containing entries of sources and checksums for each of the supported versions.

### url

`url` contains a string specifiying [URI](https://tools.ietf.org/html/rfc3986) where to download released sources.
usually, `url` has a [https](https://tools.ietf.org/html/rfc2660) scheme, but other schemes, such as [ftp](https://tools.ietf.org/html/rfc959) are accepted as well.

### sha256

[sha256](https://tools.ietf.org/html/rfc6234) is a preferred method to specify hash sum for the released sources. it allows to check the integrity of sources downloaded.
you may use an [online service](https://hash.online-convert.com/sha256-generator) to compute `sha256` sum for the given `url`.

### sha1

[sha1](https://tools.ietf.org/html/rfc3174) is an alternate method to specify hash sum, it's usage is strongly discouraged in CCI. prefer `sha256`.

### md5

[md5](https://tools.ietf.org/html/rfc1321) is an alternate method to specify hash sum, it's usage is strongly discouraged in CCI. prefer `sha256`.

### sources - use cases

there are several major ways to specify sources.

#### single source

the most straighforward format:
```
sources:
  "1.18.0":
    sha256: 820688d1e0387ff55194ae20036cbae0fb3c7d11b7c3f46492369723c01df96f
    url: https://github.com/chriskohlhoff/asio/archive/asio-1-18-0.tar.gz
```

#### single source with download mirror

sometimes it's a good idea to specify several download mirrors - some hosts are known to be unreliable or banned in certain countries:
```
sources:
  "1.2.11":
    url: [
         "https://zlib.net/zlib-1.2.11.tar.gz",
         "https://downloads.sourceforge.net/project/libpng/zlib/1.2.11/zlib-1.2.11.tar.gz",
       ]
    sha256: "c3e5e9fdd5004dcb542feda5ee4f0ff0744628baf8ed2dd5d66f8ca1197cb1a1"
```
keep in mind all the mirrors have to provide the exactly same source (e.g. no repackaging), thus using the same hash sum.

#### source code + license

certain projects provide license on its own, and released artifacts do not include it already:
```
sources:
  8.0.0:
    - url: https://github.com/approvals/ApprovalTests.cpp/releases/download/v.8.0.0/ApprovalTests.v.8.0.0.hpp
      sha256: e16a97081f8582be951d95a9d53dc611f1f5a84e117a477029890d0b34ae99d6
    - url: "https://raw.githubusercontent.com/approvals/ApprovalTests.cpp/v.8.0.0/LICENSE"
      sha256: c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4
```

#### several source code archives

certain projects may include multiple tarballs as a part of release, [OpenCV](https://opencv.org/) is an example which includes auxillary [contrib](https://github.com/opencv/opencv_contrib) archive:
```
sources:
  "4.5.0":
    - sha256: dde4bf8d6639a5d3fe34d5515eab4a15669ded609a1d622350c7ff20dace1907
      url: https://github.com/opencv/opencv/archive/4.5.0.tar.gz
    - sha256: a65f1f0b98b2c720abbf122c502044d11f427a43212d85d8d2402d7a6339edda
      url: https://github.com/opencv/opencv_contrib/archive/4.5.0.tar.gz
```

#### different source code archives per configuration

this is the most advanced and sophisticated use-case, fortunately, rarely encountered in the wild. project may provide different sources for different platforms for awkward reasons, it could be expressed as:

```
sources:
  "0066":
    "Macos":
      "apple-clang":
        "x86":
          - url: "https://naif.jpl.nasa.gov/pub/naif/misc/toolkit_N0066/C/MacIntel_OSX_AppleC_32bit/packages/cspice.tar.Z"
            sha256: "9a4b5f674ea76821c43aa9140829da4091de646ef3ce40fd5be1d09d7c37b6b3"
        "x86_64":
          - url: "https://naif.jpl.nasa.gov/pub/naif/misc/toolkit_N0066/C/MacIntel_OSX_AppleC_64bit/packages/cspice.tar.Z"
            sha256: "f5d48c4b0d558c5d71e8bf6fcdf135b0943210c1ff91f8191dfc447419a6b12e"
```

this approach requires a special code within [source](https://docs.conan.io/en/latest/reference/conanfile/methods.html#source) method to handle.

## patches

sometimes sources provided by project require patching for various reasons. `conandata.yml` may include information about patches.

### patch_file

patch file might be commited to the conan-center-index, near to the conanfile (usuaully, into the `patches` sub-directory). such patch files usually have either `.diff` or `.patch` extension.
the recommented way to generate such patches is [git format-patch](https://git-scm.com/docs/git-format-patch). the path to the patch is relative to the directory containing `conandata.yml` and `conanfile.py`.

### base_path

specifies a sub-directory in project's sources to apply patch. directory is relative to the [source_folder](https://docs.conan.io/en/latest/reference/conanfile/attributes.html?highlight=source_folder#source-folder). usually, it would be a `source_subfolder`, but could be a lower-level sub-directory (e.g. if it's a patch for the submodule),

### url

the patch could be taken from the existing resource (e.g. some patches are distributed alongside the source tarball). see `url` section of the `sources`.

### sha256

for the patch downloaded from the Internet, provides a hashsum. see `sha256` section of the `sources`.

### sha1

for the patch downloaded from the Internet, provides a hashsum. see `sha1` section of the `sources`.

### md5

for the patch downloaded from the Internet, provides a hashsum. see `md5` section of the `sources`.

### patch_type

the `patch_type` field specifies the type of the patch. in conan-center-index we currently accept only several kind of patches.

#### official

`patch_type: official` indicates the patch is distributed with source code itself. usually, this happens if release managers failed to include a critical fix to the release, but it's too much burden for them to make a new release just because of that single fix.
[example](https://www.boost.org/users/history/version_1_72_0.html) (notice the `coroutine` patch)

#### vulnerability

`patch_type: vulnerability` indicatea the patch that addresses the security issue. the patch description should include the index of CVE or CWE the patch addresses.
usually, upstream does new releases for vulnerabilities itself, but some projects are either abandoned or inactive.

#### backport

`patch_type: backport` indicates the patch backports an existing bug fix from the newer release or master branch (or equivalent, such as main/develop/trunk/etc). the patch address may be a pull request, or bug within the project's issue tracker.
backports are accepted only for bugs, but not for feature requests. usually, the following kind of problems are good candidates for backports:

- program doesn't start at all
- crash, such as segmentation fault or access violation
- hang up or deadlock
- memory leak or resource leak in general
- garbage output
- abnormal termination without a crash (e.g. just exit 1 at very beginning of the execution)
- data corruption
- use of outdated or deprecated API or library

as sources with backports don't act exactly the same as the version officially released, it may be a source of confusion for the consumers who are relying on the buggy behavior (even if it's completely wrong).
therefore, it's required to introduce a new `cci.` version for such backports, so consumers may choose to use either official version, or modified version with backport(s) included.

#### portability

`patch_type: portability` indicates the patch improves the portability of the library, e.g. adding supports of new architectures (ARM, Sparc, etc.), operation systems (FreeBSD, Android, etc.), compilers (Intel, MinGW, etc.), and other types of configurations which are not originally supported by the project.
in such cases, the patch could be adopted from another package repository (e.g. MSYS packages, Debian packages, Homebrew, FreeBSD ports, etc.).
patches of this kind are preferred to be submitted upstream first (in contrast to patch_type: conan), but it's not always possible.
some projects simply do not accept patches for platforms they don't have a build/test infrastracture. some projects are just either abandoned or inactive.

#### conan

`patch_type: conan` indicates the patch that is conan-specific, patches of such kind are usually not welcomed upstream at all, because they provide zero value outside of conan.
examples of such a patches may include modifications of build system files to allow dependencies provided by conan instead of dependencies provided by projects themselves (e.g. as submodule or just 3rd-party sub-directory) or by the system package manager (rpm/deb).
such patches, for instance, may contain variables are targets generated only by conan, but not generated normally by the build system (e.g. `CONAN_INCLUDE_DIRS`).

### patch_source

`patch_source` is an URL from where patch was taken from, https scheme is preferred, but other URLs (e.g. git/svn/hg) are also accepted if there is no alternative. what could be a patch source?

- link to the public commit in project hosting like GitHub/GitLab/BitBucket/Savanha/SourceForge/etc
- link to the Pull Request or equivalent (e.g. gerrit review)
- link to the bug tracker (such as JIRA, BugZilla, etc.)
- link to the mail list discussion
- link to the patch itself in another repository (e.g. MSYS, Debian, etc.)

for the `patch_type: portability` there might be no patch source matching the definition above. although we encourage contributors to submit all such portability fixes upstream first, it's not always possible (e.g. for projects no longer maintained), in such case link to the conan issue is a valid patch source (if there is no issue, you may create one).
for the `patch_type: conan`, it doesn't make sense to submit patch upstream, so there will be no patch source.

### patch_description

`patch_description` is an arbitrary text describing the following aspects of the patch:

- what does patch do (example - `add missing unistd.h header`)
- why is it necessary (example - `port to Android`)
- how exactly does patch achieve that (example - `update configure.ac`)

therefore, the full description may look like: `port to Android: update configure.ac adding missing unistd.h header`

## reduce

conan CI runs [special hook](https://github.com/conan-io/hooks/blob/master/hooks/conan-center.py#L590) to reduce the `conandata.yml` so it contains information specific only to the given version.
while it might be surprising for consumers that package built by conan center and package built locally (e.g. via [conan create](https://docs.conan.io/en/latest/reference/commands/creator/create.html)) don't match (have different `conandata.yml`), this approach has its own advantages.
imagine we have a recipe with conandata like:
```

sources:
  1.69.0:
    url:  "https://dl.bintray.com/boostorg/release/1.69.0/source/boost_1_69_0.tar.bz2",
    sha256: "8f32d4617390d1c2d16f26a27ab60d97807b35440d45891fa340fc2648b04406"
```
and now we want to add newer version (1.70.0), so our `conandata.yml` will look like:
```

sources:
  1.69.0:
    url:  "https://dl.bintray.com/boostorg/release/1.69.0/source/boost_1_69_0.tar.bz2"
    sha256: "8f32d4617390d1c2d16f26a27ab60d97807b35440d45891fa340fc2648b04406"
  1.70.0:
    url: "https://dl.bintray.com/boostorg/release/1.70.0/source/boost_1_70_0.tar.bz2"
    sha256: "430ae8354789de4fd19ee52f3b1f739e1fba576f0aded0897c3c2bc00fb38778"
```
as both versions (1.69.0 and 1.70.0) share the same conandata.yml, without a hook, our change would introduce a new revision for 1.69.0.
but if we want to avoid redundand revisions (and unnecessary rebuilds) while adding new version, we may reduce conandata for 1.69.0 to just contain the minimum amount of the information.
