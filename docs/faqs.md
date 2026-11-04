# FAQs

This section gathers the most common questions from the community related to packages and usability of this repository.

<!-- toc -->
## Contents

  * [What is the policy on recipe name collisions?](#what-is-the-policy-on-recipe-name-collisions)
  * [What is the policy for naming forks?](#what-is-the-policy-for-naming-forks)
  * [What is the policy on creating packages from pre-compiled binaries?](#what-is-the-policy-on-creating-packages-from-pre-compiled-binaries)
  * [Should reference names use `-` or `_`?](#should-reference-names-use---or-_)
  * [Why are CMake find/config files and pkg-config files not packaged?](#why-are-cmake-findconfig-files-and-pkg-config-files-not-packaged)
  * [Why recipes that use build tools (like CMake) that have packages in Conan Center do not use it as a build require by default?](#why-recipes-that-use-build-tools-like-cmake-that-have-packages-in-conan-center-do-not-use-it-as-a-build-require-by-default)
  * [How are rare build systems without generators packaged?](#how-are-rare-build-systems-without-generators-packaged)
  * [Are python requires allowed in the `conan-center-index`?](#are-python-requires-allowed-in-the-conan-center-index)
  * [What version should packages use for libraries without official releases?](#what-version-should-packages-use-for-libraries-without-official-releases)
  * [Is the Jenkins orchestration library publicly available?](#is-the-jenkins-orchestration-library-publicly-available)
  * [Why not x86 binaries?](#why-not-x86-binaries)
    * [But if there are no packages available, what will the x86 validation look like?](#but-if-there-are-no-packages-available-what-will-the-x86-validation-look-like)
  * [Do static libraries tend to be compiled as PIC by default?](#do-static-libraries-tend-to-be-compiled-as-pic-by-default)
  * [Why PDB files are not allowed?](#why-pdb-files-are-not-allowed)
    * [Why is there no option for PDB, as there is for fPIC?](#why-is-there-no-option-for-pdb-as-there-is-for-fpic)
    * [Doesn't this make debug builds useless?](#doesnt-this-make-debug-builds-useless)
  * [Can I remove an option from a recipe?](#can-i-remove-an-option-from-a-recipe)
  * [Can I split a project into an installer and library package?](#can-i-split-a-project-into-an-installer-and-library-package)
  * [Should recipes export a recipe's license?](#should-recipes-export-a-recipes-license)
  * [What license should I use for Public Domain?](#what-license-should-i-use-for-public-domain)
  * [What license should I use for a custom project specific license?](#what-license-should-i-use-for-a-custom-project-specific-license)
  * [How do I flag a problem to a recipe consumer?](#how-do-i-flag-a-problem-to-a-recipe-consumer)
  * [What is the policy for adding older versions of a package?](#what-is-the-policy-for-adding-older-versions-of-a-package)
  * [What is the policy for removing older versions of a package?](#what-is-the-policy-for-removing-older-versions-of-a-package)
  * [Can I install packages from the system package manager?](#can-i-install-packages-from-the-system-package-manager)
  * [Why ConanCenter does not build and execute tests in recipes](#why-conancenter-does-not-build-and-execute-tests-in-recipes)
  * [Why not add an option to build unit tests](#why-not-add-an-option-to-build-unit-tests)
  * [What is the policy for supported python versions?](#what-is-the-policy-for-supported-python-versions)
  * [How to protect my project from breaking changes in recipes?](#how-to-protect-my-project-from-breaking-changes-in-recipes)
  * [What's the policy on version ranges?](#whats-the-policy-on-version-ranges)
  * [How to consume a graph of shared libraries?](#how-to-consume-a-graph-of-shared-libraries)
  * [Can we add package which are parts of bigger projects like Boost?](#can-we-add-package-which-are-parts-of-bigger-projects-like-boost)
    * [Can I add my project which I will submit to Boost?](#can-i-add-my-project-which-i-will-submit-to-boost)
  * [Can I add options that do not affect `package_id` or the package contents](#can-i-add-options-that-do-not-affect-package_id-or-the-package-contents)


## What is the policy on recipe name collisions?

Recipes follow the `<name>/<version>` reference structure, so recipe names must be unique and unambiguous. Where a library's name is ambiguous, or clashes with another library, package or tool (even one written in another language) in a way that may cause confusion, the name may be disambiguated by including the name of the vendor or author, for example `<vendor>-<name>`. Where possible, we will aim for consistency with other repositories.

For example, `GSL` is the name of both the `Guidelines Support Library` from Microsoft and the `GNU Scientific Library` from GNU. Both libraries are commonly known as `gsl`, so the recipes should be named `ms-gsl` and `gnu-gsl` respectively.

## What is the policy for naming forks?

We will expect recipes for forks to have a name that does not cause confusion with other libraries or projects. Recipes for forks of well-known libraries will be accepted, subject to the [inclusion criteria for new recipes](adding_packages/inclusion_criteria_for_new_recipes.md). That is, we still expect evidence that the fork is in use and that it is actively maintained.

## What is the policy on creating packages from pre-compiled binaries?

The policy is that in the general case [recipes should build packages from sources](adding_packages/sources_and_patches.md#picking-the-sources), because of reproducibility and security concerns. The implication is that the sources must be publicly available, and in a format that can be consumed programmatically.

See [Picking Sources](adding_packages/sources_and_patches.md#picking-the-sources) for more information.

## Should reference names use `-` or `_`?

Recipes should stick to the original name of a library as much as possible. For example `libjpeg-turbo`, `expected-lite` and `optional-lite` have a `-` in their original names.

In the case of spaces in the name, the most common approach is to use `_` as done in `xz_utils`.

For libraries with a too generic name, like `variant`, the name of the organization can be used as prefix separated by a `-`, like `mpark-variant`, `tl-expected` or `taocpp-tuple`.

## Why are CMake find/config files and pkg-config files not packaged?

We know that using `find_package()` and relying on the CMake behavior to find the dependencies is something that should be avoided in favor of the information provided by the package manager.

Conan has an abstraction over the packages build system and description by using generators. Those generators translate the information of the dependency graph and create a suitable file that can be consumed by your build system.

In the past, we have found that the logic of some of the CMake's find/config or pkg-config files can lead to broken scenarios due to issues with:

- Transitive dependencies: The find logic of CMake can lead to link libraries with system libraries instead of the ones specified in the conanfile.
- Different build type configurations: Usually those files are not prepared to handle multi-configuration development while switching between release/debug build types for example.
- Absolute paths: Usually, those files include absolute paths that would make the package broken when shared and consumed.
- Hardcoded versions of dependencies as well as build options that make overriding dependencies from the consumer not possible.

We believe that the package manager should be the one responsible to handle this information in order to achieve a deterministic and controlled behavior.
Regarding the integration with CMake, Conan already provides ways to consume those packages in the same way by using generators like [CmakeDeps](https://docs.conan.io/2/reference/tools/cmake/cmakedeps.html) to define internal libraries of a package and generate proper CMake targets or [cmake_build_modules](https://docs.conan.io/2/examples/graph/tool_requires/use_cmake_modules.html) to package build system utilities like CMake macros.

Defining the package information in the recipe is also useful in order to consume those packages from a different build system, for example using pkg-config with the [PkgConfigDeps](https://docs.conan.io/2/reference/tools/gnu/pkgconfigdeps.html).

Finally, by not allowing these files we make packages agnostic to the consumer as the logic of those files is not in the package but in the way the consumer wants the information.

If you really think this is an issue and there is something missing to cover the use case of a library you want to contribute to ConanCenter, please do not hesitate to open an issue and we will be happy to hear your feedback.

## Why recipes that use build tools (like CMake) that have packages in Conan Center do not use it as a build require by default?

We generally consider tools like CMake as a standard tool to have installed in your system. Having the `cmake` package as a build require in **all** the recipes that use it will be an overkill, as every build requirement is installed like a requirement and takes time to download. However, `cmake` could still be useful to use in your profile:

```
[tool_requires]
cmake/[>=3.15 <4]
```

Other packages using more unusual build tools should refer to the [Dependencies - Adding Build Requirements](adding_packages/dependencies.md#build-requirements) section for more information.

## How are rare build systems without generators packaged?

The C++ ecosystem has a lot of rare, unique and obscure build systems. Some of these are available in ConanCenter but they do not have built-in generators from the main Conan client.
The recipe is expected to encode the specifics of the build system, mapping the `settings`, `options` for the binary configuration, and also mapping `self.dependencies` so the build system can locate the dependencies libraries as required.
For these cases, contributors are asked to help reviewers as much as possible as it's likely we will not have expertise.

In Conan 2.x is possible to use [custom generators](https://docs.conan.io/2/reference/extensions/custom_generators.html). But this feature is not allowed in conan-center-index.

For quality assurance the build service is expected to be green and the hooks will ensure the package contents match what is expected given the options. These recipes are more likely to have
inconsistency with other recipes but make for excellent contributions.

## Are python requires allowed in the `conan-center-index`?

Unless they are a general and extended utility in recipes (in which case, we should study its inclusion in the Conan tools module), python requires are not allowed in `conan-center-index` repository.

## What version should packages use for libraries without official releases?

When proposing a new recipe for a library to be included in the repository, subject to the [inclusion criteria for new recipes](adding_packages/inclusion_criteria_for_new_recipes.md), a library without formal, versioned releases will be considered for inclusion if it explicitly states that it follows a "live at head" approach (for example, in its README or contributing guidelines). A library that has no releases and does not state a policy is more likely to be flagged as not ready yet to be included in Conan Center.

For libraries that qualify, we will look at how other package repositories and package managers version the same library, and use that to define a versioning scheme for the recipe. Where no better convention exists, the [ConanCenter specific version format based on a timestamp](adding_packages/conanfile_attributes.md#conancenter-specific-releases-format) will apply.

Be aware that in some cases the lack of a usable versioning scheme can be a blocker for inclusion. For example, this can happen if upstream does not offer checksum-stable packaged tarballs with the source code (see [Picking the Sources](adding_packages/sources_and_patches.md#picking-the-sources)).

## Is the Jenkins orchestration library publicly available?

Currently, the Jenkins orchestration library for this build service is not available. We believe this solution is too specific for this purpose, as we are massively building binaries for many configurations and the main purpose of a CI system with Conan in an organization should be to rebuild only the need packages. However, we know this could be interesting for organizations in order to learn new approaches for CI flows. We will release this information and CI flow recommendations as soon as possible.

## Why not x86 binaries?

Only the x86_64 architecture is available for download, the rest must be built from sources. The reasons behind this decision are:

* Few users need different pre-built packages that are not x86_64 packages, this number is less than 10% of total users (data obtained through the download counter from Bintray), and tends to decrease over the years;
* Some OS are putting the x86 as obsolete, examples [macOS](https://developer.apple.com/documentation/macos-release-notes/macos-catalina-10_15-release-notes) and Ubuntu 20.04;
* For security reasons, most companies build their own packages from sources, even if they already have a pre-built version available, which further reduces the need for extra configurations;
* Each recipe results in several packages, and this is only for x86_64, but not all packages are used, some settings remain with zero downloads throughout their life. So, imagine adding more settings that will rarely be used, but that will consume more resources as time and storage, this leaves us in an impractical situation.

### But if there are no packages available, what will the x86 validation look like?

As stated earlier, any increase in the number of configurations will result in an impractical scenario. In addition, more validations require more review time for a recipe, which would increase the time for all PRs, delaying the release of a new package. For these reasons, x86 is not validated by the CCI.

We often receive new fixes and improvements to the recipes already available for x86_64, including help for other architectures like x86 and ARM. In addition, we also receive new cases of bugs, for recipes that do not work on a certain platform, but that are necessary for use, which is important to understand where we should put more effort. So we believe that the best way to maintain and add support for other architectures is through the community.

## Do static libraries tend to be compiled as PIC by default?

Yes! You can learn more about default options in [Packaging Policy](adding_packages/conanfile_attributes.md#predefined-options-and-known-defaults).

## Why PDB files are not allowed?

The project initially decided not to support the PDB files primarily due to the size of the final package, which could add an exaggerated size and not even used by users. In addition, PDB files need the source code to perform the debugging and even follow the path in which it was created and not the one used by the user, which makes it difficult to use when compared to the regular development flow with the IDE.

However, there are ways to get around this, one of them is through the [/Z7](https://docs.microsoft.com/en-us/cpp/build/reference/z7-zi-zi-debug-information-format) compilation flag, which can be passed through [environment variables](https://docs.microsoft.com/en-us/cpp/build/reference/cl-environment-variables). You can use your [profile](https://docs.conan.io/2/reference/config_files/profiles.html) to customize your compiler command line.

### Why is there no option for PDB, as there is for fPIC?

Adding one more common option, it seems the most simple and obvious solution, but it contains a side effect already seen with fPIC. It is necessary to manage the entire recipe, it has become a Boilerplate. So, adding PDB would be one more point to be reviewed for each recipe. In addition, in the future new options could arise, such as sanity or benchmark, further inflating the recipes. For this reason, a new option will not be added. However, the inclusion of the PDB files is discussed in issue [#1982](https://github.com/conan-io/conan-center-index/issues/1982) and there are some ideas for making this possible through a new feature. If you want to comment on the subject, please visit issue.

### Doesn't this make debug builds useless?

No. The PDBs are only needed to debug dependency code. By providing the libraries you are able to link and build your application and debug your own code.
This is by far the more common scenario which we want to enable.

## Can I remove an option from a recipe?

It's preferable to leave all options (ie. not removing them) because it may break other packages which require those deleted options.
Prefer the deprecation path with a mapping from old options to new ones:

* Add "deprecated" as option value
* Set "deprecated" as default option
* Check the option value, if the value is different from "deprecated", raise a warning
* Remove the option from Package ID

```python
options = {"foobar": [True, False, "deprecated"]}
default_options = {"foobar": "deprecated"}

def configure(self):
    if self.options.foobar != "deprecated":
        self.output.warning("foobar option is deprecated, do not use anymore.")

def package_id(self):
    del self.info.options.foobar
```

This is the safest way, users will be warned of deprecation and their projects will not risk breaking.
As additional examples, take a look on follow recipes: [dcmtk](https://github.com/conan-io/conan-center-index/blob/5e6089005f0bb66cd16db7b0e5f37f5081c7820c/recipes/dcmtk/all/conanfile.py#L24), [gtsam](https://github.com/conan-io/conan-center-index/blob/f7f18ab050e5d97fac70932b0ba4c115a930958c/recipes/gtsam/all/conanfile.py#L40)
and [libcurl](https://github.com/conan-io/conan-center-index/blob/f834ee1c82564199fdd9ca2f95231693c1a7136a/recipes/libcurl/all/conanfile.py#L24).

However, if logic is too complex (this is subjective and depends on the Conan review team) then just remove the option.
After one month, we will welcome a PR removing the option that was deprecated.

## Can I split a project into an installer and library package?

No. Some projects provide more than a simple library, but also applications. For those projects, both libraries and executables should be kept together under the same Conan package. In the past, we tried to separate popular projects, like Protobuf, and it proved to be a complex and hard task to be maintained, requiring custom patches to disable parts of the building. Also, with the [context](https://docs.conan.io/2/reference/commands/install.html#reference-commands-install-composition) feature, we can use the same package as build requirement, for the same build platform, and as a regular requirement, for the host platform, when cross-building. It's recommended using 2 profiles in that case, one for build platform (where the compilation tools are being executed) and one for host platform (where the generated binaries will run).

## Should recipes export a recipe's license?

No, recipes do not need to export a recipe license. Recipes and all files contributed to this repository are licensed under the license in the root of the repository. Using any recipe from this repository or directly from conan-center implies the same licensing.

## What license should I use for Public Domain?

See [License Attribute](adding_packages/conanfile_attributes.md#license-attribute) for details.

## What license should I use for a custom project specific license?

See [License Attribute](adding_packages/conanfile_attributes.md#license-attribute) for details.

## How do I flag a problem to a recipe consumer?

Regardless of why, if the recipe detects a problem where binaries might not be generated correctly, an exception must be raised. This to prevent the publishing
incorrect packages which do not work as intended. Use `ConanInvalidConfiguration` which is specially support in ConanCenter.

```py
raise ConanInvalidConfiguration(f"The project {self.ref} requires liba.enable_feature=True. See <url_to_upstream>")
```

You should not be using the `self.output.warning` and it is not enough to alter consumers or stop the build service.

Also, need to point upstream's issue/PR related to the same problem. In case it's a limitation in the recipe, the same should be clear and be merged without full support:

```py
raise ConanInvalidConfiguration(f"{self.ref} Conan recipe does not support Windows. Contributions are welcome!")
```

## What is the policy for adding older versions of a package?

See [Adding older versions](adding_packages/sources_and_patches.md#adding-old-versions) for details.

## What is the policy for removing older versions of a package?

See [Removing older versions](adding_packages/sources_and_patches.md#removing-old-versions) for details.

## Can I install packages from the system package manager?

It depends. You can not mix both regular projects with system packages, but you can provide package wrappers for system packages. However, Conan can not track system packages, like their version and options, which creates a fragile situation where affects libraries and binaries built in your package but can not be totally reproduced.

Also, system package managers require administrator permission to install packages, which is not always possible and may break limited users. Moreover, more than one Conan package may require the same system package and there is no way to track their mutual usage.

There are exceptions where some projects are closer to system drivers or hardware and packaging as a regular library could result
in an incompatible Conan package. To deal with those cases, you are allowed to provide an exclusive Conan package which only installs system packages, see the [How-to](adding_packages/build_and_package.md#system-packages) for more.

## Why ConanCenter does **not** build and execute tests in recipes

<!-- ref https://github.com/conan-io/conan-center-index/pull/5405#issuecomment-854618305 -->

There are different motivations:

- time and resources: adding the build time required by the test suite plus execution time can increase our building times significantly across the 100+ configurations.
- ConanCenter is a service that builds binaries for the community for existing library versions, this is not an integration system to test the libraries.

## Why not add an option to build unit tests

- Adding a testing option will change the package ID, but will not provide different packaged binaries
- Use the configuration [skip_test](adding_packages/conanfile_attributes.md#options-to-avoid) to define the testing behavior.

## What is the policy for supported python versions?

`Python 2.7` and earlier is not supported by the ConanCenter, as it's already [EOL](https://www.python.org/doc/sunset-python-2/).

`Python 3.6` and earlier is also not supported by the ConanCenter, as it's already [EOL](https://peps.python.org/pep-0494/#lifespan).

Versions `Python 3.7+` onwards are currently supported by the infrastructure and the recipes.

Our [docker images](https://github.com/conan-io/conan-docker-tools) use `Python 3.7.13+` ATM.

Windows agents currently use `Python 3.7.9+`. macOS agents use version `Python 3.7.12+`.

The version run by our agents and docker images is a subject to change, as security updates to the Python are released, or they enter EOL.

Additional concerns about supported versions within conan ecosystem (not just ConanCenter, but client itself and other tools) are documented in [tribe](https://github.com/conan-io/tribe/pull/3).

For ConanCenter, besides security, there are various concerns about critical features provided by the Python interpreter, include its syntax and the standard library, e.g.:

- LZMA compression support
- Unicode awareness
- long-path awareness

Right now, only the [CPython](https://github.com/python/cpython) flavor of the interpreter is supported (e.g. we never tested recipes work with IronPython, JPython, Cython, etc.).

In addition, we support only 64-bit builds of the interpreter (amd64/x86_64 architecture) - 32-bit builds (x86) are not supported and not installed on the agents.

There are no guarantees that recipes will work correctly in future Python versions having breaking changes to the interpreter,
 as we don't test all the possible combinations (and probably will never be). Patches are welcomed if problems are found.

## How to protect my project from breaking changes in recipes?

This repository and the CI building recipes is continuously pushing to new Conan versions,
sometimes adopting new features as soon as they are released
([Conan client changelog](https://docs.conan.io/2/changelog.html)).

You should expect that latest revision of recipes can introduce breaking changes and new
features that will be broken unless you also upgrade Conan client (and sometimes you will
need to modify your project if the recipe changes the binaries, flags,... it provides).

To isolate from these changes there are different strategies you can follow.
Keep reading in the [consuming recipes section](consuming_recipes.md#isolate-your-project-from-upstream-changes).

## What's the policy on version ranges?

Version ranges are currently allowed on a handful of dependencies, but not for general use.
See [Dependencies Version Ranges](adding_packages/dependencies.md#version-ranges) for additional details.

## How to consume a graph of shared libraries?

When the CI builds packages with the option `*/*:shared=True`, this option is applied not only to the package being created but also to its requirements.
Since the default value for the shared option is typically `False`, you can generally expect that the dependency graph will consist of static libraries,
except for packages specifically defined with `package_type = "shared-library"`.

To work with a graph that includes only shared libraries, you must explicitly set the `-o */*:shared=True` option in your conan install command.
This ensures that the necessary shared libraries are included in your build environment.

## Can we add package which are parts of bigger projects like Boost?

Sadly no. There have been many efforts in the past and we feel it's not sustainable given the number of combinations of libraries and version.
See #14660 for recent discussions. There is one main "boost" recipe with many versions maintained. Adding boost libraries with no dependencies
just opens the door to graph resolution problems and once available allows for dependent libraries to be added.

In order to avoid this the sole permutation which is permissible is when the project does not package any headers under the `boost/` folder, does not use the boost namespace
and does not install libraries with the boost prefix.

### Can I add my project which I will submit to Boost?

Yes, but make sure it does not have Boost in the name. Use the [`author-name` convention](https://github.com/conan-io/conan-center-index/blob/master/docs/faqs.md#what-is-the-policy-on-recipe-name-collisions) so there are no conflicts. In addition to follow the rules outlined above.

**NOTE**: In case you have no intention to submit to Boost, then you can use the project name as is (e.g `boost-foobar`).

## Can I add options that do not affect `package_id` or the package contents

Generally no, these sorts of options can most likely be set from a profile or downstream recipes. However if the project supports this option from its build script
and would otherwise dynamically embed this into the CMake config files or generated pkg-config files then it should be allowed.

Doing so requires [deleting the option from the `package_id`](adding_packages/conanfile_attributes.md#removing-from-package_id).
