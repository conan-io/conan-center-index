# Adding Packages to ConanCenter

ConanCenterIndex aims to provide the best quality packages of any open source project.
Any C/C++ project can be made available by contributing a "recipe".

Getting started is easy. Try building an existing package with our [developing recipes](../developing_recipes_locally.md) tutorial.
To deepen you understanding, start with the [How to provide a good recipe](#how-to-provide-a-good-recipe) section.
You can follow the three steps (:one: :two: :three:) described below! :tada:

<!-- toc -->
## Contents

  * [Request access](#request-access)
  * [Inactivity and user removal](#inactivity-and-user-removal)
  * [Submitting a Package](#submitting-a-package)
    * [The Build Service](#the-build-service)
  * [Recipe files structure](#recipe-files-structure)
    * [`config.yml`](#configyml)
    * [`conandata.yml`](#conandatayml)
    * [The _recipe folder_: `conanfile.py`](#the-_recipe-folder_-conanfilepy)
    * [Test Folders](#test-folders)
  * [How to provide a good recipe](#how-to-provide-a-good-recipe)
    * [Header Only](#header-only)
    * [CMake](#cmake)
      * [Components](#components)
    * [Autotools](#autotools)
      * [Components](#components-1)
    * [No Upstream Build Scripts](#no-upstream-build-scripts)
    * [System Packages](#system-packages)
    * [Verifying Dependency Version](#verifying-dependency-version)
    * [Verifying Dependency Options](#verifying-dependency-options)
  * [Test the recipe locally](#test-the-recipe-locally)
    * [Hooks](#hooks)
    * [Linters](#linters)<!-- endToc -->

## Request access

:one: The first step to add packages to ConanCenter is requesting access. To enroll in ConanCenter repository, please write a comment
requesting access in this GitHub [issue](https://github.com/conan-io/conan-center-index/issues/4). Feel free to introduce yourself and
your motivation to join ConanCenter community.

This process helps ConanCenter against spam and malicious code. The process is not not automated on purpose and the requests are generally approved
on a weekly basis.

> **Note** The requests are reviewed manually, checking the GitHub profile activity of the requester to avoid any misuse of the service.
> All interactions are subject to the expectations of the [code of conduct](../code_of_conduct.md). Any misuse or inappropriate behavior are subject
> to the same principals.

When submitting a pull request for the first time, you will be prompted to sign the [CLA](../CONTRIBUTOR_LICENSE_AGREEMENT.md) for your code contributions. You can view your signed CLA's by going to <https://cla-assistant.io/> and signing in.

## Inactivity and user removal

For security reasons related to the CI, when a user no longer contributes for a long period, it will be considered inactive and removed from the authorized user's list.
For now, it's configured for **4 months**, and it's computed based on the latest commit, not comments or opened issues.
After that time, the CI bot will ask to remove the user name from the authorized users' list through the access request PR, which occurs a few times every week.
In case you are interested in coming back, please, ask again to be included in the issue [#4](https://github.com/conan-io/conan-center-index/issues/4), the process will be precise like for newcomers.

## Submitting a Package

:two: To contribute a package, you can submit a [Pull Request](https://github.com/conan-io/conan-center-index/pulls) to this GitHub repository https://github.com/conan-io/conan-center-index.

The specific steps to add new packages are:

* Fork the [conan-center-index](https://github.com/conan-io/conan-center-index) git repository, and then clone it locally.
* Copy a template from [package_templates](../package_templates) folder in the recipes/ folder and rename it to the project name (it should be lower-case). Read templates [documentation](../package_templates/README.md) to find more information.
* Make sure you are using the latest [Conan client](https://conan.io/downloads) version, as recipes might evolve introducing features of the newer Conan releases.
* Commit and Push to GitHub then submit a pull request.
* Our automated build service will build 100+ different configurations, and provide messages that indicate if there were any issues found during the pull request on GitHub.

:three: When the pull request is [reviewed and merged](../review_process.md), those packages are published to [JFrog ConanCenter](https://conan.io/center/) and available for everyone.

### The Build Service

The **build service** associated to this repo will generate binary packages automatically for the most common platforms and compilers. See [the Supported Platforms and Configurations page](../supported_platforms_and_configurations.md) for a list of generated configurations. For a C++ library, the system is currently generating more than 100 binary packages.

> ⚠️ **Note**: This not a testing service, it is a binary building service for package **released**. Unit tests shouldn't be built nor run in recipes by default, see the [FAQs](../faqs.md#why-conancenter-does-not-build-and-execute-tests-in-recipes) for more. Before submitting a pull request, please ensure that it works locally for some configurations.

- The CI bot will start a new build only after the author is approved. Your PR may be reviewed in the mean time, but is not guaranteed.
- The CI system will also report with messages in the PR any error in the process, even linking to the logs to see more details and debug.

The pipeline will report errors and build logs by creating a comment in the pull-request after every commit. The message will include links to the logs for inspecting.

Packages generated and uploaded by this build service don't include any _user_ or _channel_ (existing references with any `@user/channel` should be considered as deprecated in favor of packages without it). Once the packages are uploaded, you will be able to install them using the reference as `name/version` (requires Conan >= 1.21): `conan install cmake/3.18.2@`.

## Recipe files structure

Every entry in the `recipes` folder contains all the files required by Conan to create the binaries for all the versions of one library. Those
files don't depend on any other file in the repository (we are not using `python_requires`) and every pull-request can modify only one of those
folders at a time.

This is the canonical structure of one of these folders, where the same `conanfile.py` recipe is suitable to build all the versions of the library:

```
.
+-- recipes
|   +-- library_name/
|       +-- config.yml
|       +-- all/
|           +-- conanfile.py
|           +-- conandata.yml
|           +-- patches/
|               +-- add-missing-string-header-2.0.0.patch
|           +-- test_package/
|               +-- conanfile.py
|               +-- CMakeLists.txt
|               +-- test_package.cpp
|           +-- test_v1_package/
|               +-- conanfile.py
|               +-- CMakeLists.txt
```

If it becomes too complex to maintain the logic for all the versions in a single `conanfile.py`, it is possible to split the folder `all` into
two or more folders, dedicated to different versions, each one with its own `conanfile.py` recipe. In any case, those folders should replicate the
same structure.

### `config.yml`

This file lists the versions and the folders where they are located:

```yml
versions:
  "1.1.0":
    folder: 1.x.x
  "1.1.1":
    folder: 1.x.x
  "2.0.0":
    folder: all
  "2.1.0":
    folder: all
```


### `conandata.yml`

This file lists **all the sources that are needed to build the package**: source code, patch files, license files,... any file that will be used by the recipe
should be listed here. The file is organized into two sections, `sources` and `patches`, each one of them contains the files that are required
for each version of the library. All the files that are downloaded from the internet should include a checksum, so we can validate that
they are not changed.

A detailed breakdown of all the fields can be found in [conandata_yml_format.md](conandata_yml_format.md). We **strongly** encourage adding the [patch fields](conandata_yml_format.md#patches-fields) to help track where patches come from and what issue they solve.

Inside the `conanfile.py` recipe, this data is available in a `self.conan_data` attribute that can be used as follows:

```py
def export_sources(self):
    export_conandata_patches(self)

def source(self):
    files.get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

def build(self):
    files.apply_conandata_patches(self)
    [...]
```

### The _recipe folder_: `conanfile.py`

The main files in this repository are the `conanfile.py` ones that contain the logic to build the libraries from sources for all the configurations,
as we said before there can be one single recipe suitable for all the versions inside the `all` folder, or there can be several recipes targeting
different versions in different folders. For maintenance reasons, we prefer to have only one recipe, but sometimes the extra effort doesn't worth
it and it makes sense to split and duplicate it, there is no common rule for it.

Together with the recipe, there can be other files that are needed to build the library: patches, other files related to build systems,
... all these files will usually be listed in `exports_sources`  and used during the build process.

Also, **every `conanfile.py` should be accompanied by one or several folder to test the generated packages** as we will see below.

### Test Folders

All the packages in this repository need to be tested before they join ConanCenter. A `test_package/` folder with its corresponding `conanfile.py` and
a minimal project to test the package is strictly required. You can read about it in the
[Conan documentation](https://docs.conan.io/en/latest/creating_packages/getting_started.html).

Learn more about the ConanCenterIndex requirements in the [test packages](test_packages.md) document.

## How to provide a good recipe

The [recipes](https://github.com/conan-io/conan-center-index/tree/master/recipes) available in CCI can be used as good examples, you can use them as the base for your recipe. However it is important to note Conan features change over time and our best practices evolve so some minor details may be out of date due to the vast number of recipes.

### Header Only

If you are looking for header-only projects, you can take a look on [header-only template](../package_templates/header_only).
Also, Conan Docs has a section about [how to package header-only libraries](https://docs.conan.io/en/latest/howtos/header_only.html).

### CMake

For C/C++ projects which use CMake for building, you can take a look on [cmake package template](../package_templates/cmake_package).

#### Components

Another common use case for CMake based projects, both header only and compiled, is _modeling components_ to match the `find_package` and export the correct targets from Conan's generators. A basic examples of this is [cpu_features](https://github.com/conan-io/conan-center-index/blob/master/recipes/cpu_features/all/conanfile.py), a moderate/intermediate example is [cpprestsdk](https://github.com/conan-io/conan-center-index/blob/master/recipes/cpprestsdk/all/conanfile.py), and a very complex example is [OpenCV](https://github.com/conan-io/conan-center-index/blob/master/recipes/opencv/4.x/conanfile.py).

### Autotools

However, if you need to use autotools for building, you can take a look on [libalsa](https://github.com/conan-io/conan-center-index/blob/master/recipes/libalsa/all/conanfile.py), [kmod](https://github.com/conan-io/conan-center-index/blob/master/recipes/kmod/all/conanfile.py), [libcap](https://github.com/conan-io/conan-center-index/blob/master/recipes/libcap/all/conanfile.py).

#### Components

Many projects offer **pkg-config**'s `*.pc` files which need to be modeled using components. A prime example of this is [Wayland](https://github.com/conan-io/conan-center-index/blob/master/recipes/wayland/all/conanfile.py).

### No Upstream Build Scripts

For cases where a project only offers source files, but not a build script, you can add CMake support, but first, contact the upstream and open a PR offering building support. If it's rejected because the author doesn't want any kind of build script, or the project is abandoned, CCI can accept your build script. Take a look at [Bzip2](https://github.com/conan-io/conan-center-index/blob/master/recipes/bzip2/all/CMakeLists.txt) and [DirectShowBaseClasses](https://github.com/conan-io/conan-center-index/blob/master/recipes/directshowbaseclasses/all/CMakeLists.txt) as examples.

### System Packages

> :information_source: For exceptional cases where only system packages can be used and a regular Conan package may result in an incompatible and fragile package, a separated system package may be created. See the [FAQs](../faqs.md#can-i-install-packages-from-the-system-package-manager) for more.

The [SystemPackageTool](https://docs.conan.io/en/latest/reference/conanfile/methods.html#systempackagetool) can easily manage a system package manager (e.g. apt,
pacman, brew, choco) and install packages which are missing on Conan Center but available for most distributions. It is key to correctly fill in the `cpp_info` for the consumers of a system package to have access to whatever was installed.

As example there is [xorg](https://github.com/conan-io/conan-center-index/blob/master/recipes/xorg/all/conanfile.py). Also, it will require an exception rule for [conan-center hook](https://github.com/conan-io/hooks#conan-center), a [pull request](https://github.com/conan-io/hooks/pulls) should be open to allow it over the KB-H032.

### Verifying Dependency Version

Some project requirements need to respect a version constraint. This can be enforced in a recipe by accessing the [`dependencies`](https://docs.conan.io/en/latest/reference/conanfile/dependencies.html) attribute.
An example of this can be found in the [fcl recipe](https://github.com/conan-io/conan-center-index/blob/1b6b496fe9a9be4714f8a0db45274c29b0314fe3/recipes/fcl/all/conanfile.py#L80).

```py
def validate(self):
    foobar = self.dependencies["foobar"]
    if self.info.options.shared and Version(foobar.ref.version) < "1.2":
        raise ConanInvalidConfiguration(f"{self.ref} requires 'foobar' >=1.2 to be built as shared.")
```

### Verifying Dependency Options

Certain projects are dependant on the configuration (a.k.a options) of a dependency. This can be enforced in a recipe by accessing the [`options`](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#options) attribute.
An example of this can be found in the [sdl_image recipe](https://github.com/conan-io/conan-center-index/blob/1b6b496fe9a9be4714f8a0db45274c29b0314fe3/recipes/sdl_image/all/conanfile.py#L93).

```py
    def validate(self):
        foobar = self.dependencies["foobar"]
        if not foobar.options.enable_feature:
            raise ConanInvalidConfiguration(f"The project {self.ref} requires foobar:enable_feature=True.")
```

## Test the recipe locally

### Hooks

The system will use the [conan-center hook](https://github.com/conan-io/hooks) to perform some quality checks. These are required for the
the CI to merge any pull request.

Follow the [Developing Recipes Locally](../developing_recipes_locally.md#installing-the-conancenter-hooks) guide for instructions.

Go to the [Error Knowledge Base](../error_knowledge_base.md) page to know more about Conan Center hook errors.
Some common errors related to Conan can be found on the [troubleshooting](https://docs.conan.io/en/latest/faq/troubleshooting.html) section.

### Linters

Linters are always executed by Github actions to validate parts of your recipe, for instance, if it uses migrated Conan tools imports.
All executed linters are documented in [linters.md](../linters.md).
Check the [Developing Recipes](../developing_recipes_locally.md#running-the-python-linters) page for running them locally.
