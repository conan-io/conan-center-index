# Adding Packages to ConanCenter

The [conan-center-index](https://github.com/conan-io/conan-center-index) (this repository) contains recipes for the remote [JFrog ConanCenter](https://conan.io/center/).
This remote is added by default to a clean installation of the Conan client. Recipes are contributed by opening pull requests as explained in the sections below.
When pull requests are merged, the CI will upload the generated packages to the [conancenter](https://conan.io/center/) remote.

<!-- toc -->
## Contents

  * [Request access](#request-access)
  * [Submitting a Package](#submitting-a-package)
    * [The Build Service](#the-build-service)
  * [Recipe files structure](#recipe-files-structure)
    * [`config.yml`](#configyml)
    * [`conandata.yml`](#conandatayml)
    * [The _recipe folder_: `conanfile.py`](#the-_recipe-folder_-conanfilepy)
    * [The test package folders: `test_package` and `test_<something>`](#the-test-package-folders-test_package-and-test_something)
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
    * [Updating conan hooks on your machine](#updating-conan-hooks-on-your-machine)
  * [Debugging failed builds](#debugging-failed-builds)<!-- endToc -->

## Request access

:one: The first step to add packages to ConanCenter is requesting access. To enroll in ConanCenter repository, please write a comment
requesting access in this GitHub [issue](https://github.com/conan-io/conan-center-index/issues/4). Feel free to introduce yourself and
your motivation to join ConanCenter.

This process helps conan-center-index against spam and malicious code. The process is not not automated on purpose and the requests are generally approved on a weekly basis.

> :warning: The requests are reviewed manually, checking the GitHub profile activity of the requester to avoid a misuse of the service. In case of detecting a misuse or inappropriate behavior, the requester will be dropped from the authorized users list and at last instance even banned from the repository.

## Submitting a Package

:two: To contribute a package, you can submit a [Pull Request](https://github.com/conan-io/conan-center-index/pulls) to this GitHub repository https://github.com/conan-io/conan-center-index.

The specific steps to add new packages are:
* Fork the [conan-center-index](https://github.com/conan-io/conan-center-index) git repository, and then clone it locally.
* Create a new folder with the Conan package recipe (`conanfile.py`) in the correct folder.
* Make sure you are using the latest [Conan client](https://conan.io/downloads) version, as recipes might evolve introducing features of the newer Conan releases.
* Commit and Push to GitHub then submit a pull request.
* Our automated build service will build 100+ different configurations, and provide messages that indicate if there were any issues found during the pull request on GitHub.

:three: When the pull request is [reviewed and merged](review_process.md), those packages are published to [JFrog ConanCenter](https://conan.io/center/) and available for everyone.

### The Build Service

The **build service** associated to this repo will generate binary packages automatically for the most common platforms and compilers. See [the Supported Platforms and Configurations page](supported_platforms_and_configurations.md) for a list of generated configurations. For a C++ library, the system is currently generating more than 100 binary packages.

> ⚠️ **Note**: This not a testing service, it is a binary building service for package **released**. Unit tests shouldn't be built nor run in recipes by default, see the [FAQs](faqs.md#why-conancenter-does-not-build-and-execute-tests-in-recipes) for more. Before submitting a pull request, please ensure that it works locally for some configurations.

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
|           +-- test_package/
|               +-- conanfile.py
|               +-- CMakeLists.txt
|               +-- main.cpp
```

If it becomes too complex to maintain the logic for all the versions in a single `conanfile.py`, it is possible to split the folder `all` into
two or more folders, dedicated to different versions, each one with its own `conanfile.py` recipe. In any case, those folders should replicate the
same structure.

### `config.yml`

This file lists the versions and the folders where they are located (if there are more than a single `all` folder):

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

This file lists **all the sources that are needed to build the package**: source code, license files,... any file that will be used by the recipe
should be listed here. The file is organized into two sections, `sources` and `patches`, each one of them contains the files that are required
for each version of the library. All the files that are downloaded from the internet should include a checksum, so we can validate that
they are not changed:

```yml
sources:
  "1.1.0":
    url: "https://www.url.org/source/mylib-1.0.0.tar.gz"
    sha256: "8c48baf3babe0d505d16cfc0cf272589c66d3624264098213db0fb00034728e9"
  "1.1.1":
    url: "https://www.url.org/source/mylib-1.0.1.tar.gz"
    sha256: "15b6393c20030aab02c8e2fe0243cb1d1d18062f6c095d67bca91871dc7f324a"
patches:
  "1.1.1":
    - patch_file: "patches/1.1.1-001-simpler-cmakelists.patch"
      base_path: "source_subfolder"
```

Inside the `conanfile.py` recipe, this data is available in a `self.conan_data` attribute that can be used as follows:

```py
def source(self):
     tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

def build(self):
    for patch in self.conan_data.get("patches", {}).get(self.version, []):
        tools.patch(**patch)
    [...]
```

### The _recipe folder_: `conanfile.py`

The main files in this repository are the `conanfile.py` ones that contain the logic to build the libraries from sources for all the configurations,
as we said before there can be one single recipe suitable for all the versions inside the `all` folder, or there can be several recipes targetting
different versions in different folders. For mainteinance reasons, we prefer to have only one recipe, but sometimes the extra effort doesn't worth
it and it makes sense to split and duplicate it, there is no common rule for it.

Together with the recipe, there can be other files that are needed to build the library: patches, other files related to build systems (many recipes
include a `CMakeLists.txt` to run some Conan logic before using the one from the library),... all these files will usually be listed in the
`exports_sources` attribute and used during the build process.

Also, **every `conanfile.py` should be accompanied by one or several folder to test the generated packages** as we will see below.

### The test package folders: `test_package` and `test_<something>`

All the packages in this repository need to be tested before they join ConanCenter. A `test_package` folder with its corresponding `conanfile.py` and
a minimal project to test the package is strictly required. You can read about it in the
[Conan documentation](https://docs.conan.io/en/latest/creating_packages/getting_started.html#the-test-package-folder).

Sometimes it is useful to test the package using different build systems (CMake, Autotools,...). Instead of adding complex logic to one
`test_package/conanfile.py` file, it is better to add another `test_<something>/conanfile.py` file with a minimal example for that build system. That
way the examples will be short and easy to understand and maintain. In some other situations it could be useful to test different Conan generators
(`cmake_find_package`, `CMakeDeps`,...) using different folders and `conanfile.py` files ([see example](https://github.com/conan-io/conan-center-index/tree/master/recipes/fmt/all)).

When using more than one `test_<something>` folder, create a different project for each of them to keep the content of the `conanfile.py` and the
project files as simple as possible, without the need of extra logic to handle different scenarios.

```
.
+-- recipes
|   +-- library_name/
|       +-- config.yml
|       +-- all/
|           +-- conanfile.py
|           +-- conandata.yml
|           +-- test_package/
|               +-- conanfile.py
|               +-- CMakeLists.txt
|               +-- main.cpp
|           +-- test_cmakedeps/
|               +-- conanfile.py
|               +-- CMakeLists.txt
|               +-- conanfile.py
```

The CI will explore all the folders and run the tests for the ones matching `test_*/conanfile.py` pattern. You can find the output of all
of them together in the testing logs.

> **Note.-** If, for any reason, it is useful to write a test that should only be checked using Conan v1, you can do so by using the pattern
> `test_v1_*/conanfile.py` for the folder. Please, have a look to [linter notes](v2_linter.md) to know how to prevent the linter from
> checking these files.

> Remember that the `test_<package>` recipes should **test the package configuration that has just been generated** for the _host_ context, otherwise
> it will fail in crossbuilding scenarios.


## How to provide a good recipe

The [recipes](https://github.com/conan-io/conan-center-index/tree/master/recipes) available in CCI can be used as good examples, you can use them as the base for your recipe. However it is important to note Conan features change over time and our best practices evolve so some minor details may be out of date due to the vast number of recipes.

### Header Only

If you are looking for header-only projects, you can take a look on [rapidjson](https://github.com/conan-io/conan-center-index/blob/master/recipes/rapidjson/all/conanfile.py), [rapidxml](https://github.com/conan-io/conan-center-index/blob/master/recipes/rapidxml/all/conanfile.py), and [nuklear](https://github.com/conan-io/conan-center-index/blob/master/recipes/nuklear/all/conanfile.py). Also, Conan Docs has a section about [how to package header-only libraries](https://docs.conan.io/en/latest/howtos/header_only.html).

### CMake

For C/C++ projects which use CMake for building, you can take a look on [szip](https://github.com/conan-io/conan-center-index/blob/master/recipes/szip/all/conanfile.py) and [recastnavigation](https://github.com/conan-io/conan-center-index/blob/master/recipes/recastnavigation/all/conanfile.py).

#### Components

Another common use case for CMake based projects, both header only and compiled, is _modeling components_ to match the `find_package` and export the correct targets from Conan's generators. A basic examples of this is [cpu_features](https://github.com/conan-io/conan-center-index/blob/master/recipes/cpu_features/all/conanfile.py), a moderate/intermediate example is [cpprestsdk](https://github.com/conan-io/conan-center-index/blob/master/recipes/cpprestsdk/all/conanfile.py), and a very complex example is [OpenCV](https://github.com/conan-io/conan-center-index/blob/master/recipes/opencv/4.x/conanfile.py).

### Autotools

However, if you need to use autotools for building, you can take a look on [mpc](https://github.com/conan-io/conan-center-index/blob/master/recipes/mpc/all/conanfile.py), [libatomic_ops](https://github.com/conan-io/conan-center-index/blob/master/recipes/libatomic_ops/all/conanfile.py), [libev](https://github.com/conan-io/conan-center-index/blob/master/recipes/libev/all/conanfile.py).

#### Components

Many projects offer **pkg-config**'s `*.pc` files which need to be modeled using components. A prime example of this is [Wayland](https://github.com/conan-io/conan-center-index/blob/master/recipes/wayland/all/conanfile.py).

### No Upstream Build Scripts

For cases where a project only offers source files, but not a build script, you can add CMake support, but first, contact the upstream and open a PR offering building support. If it's rejected because the author doesn't want any kind of build script, or the project is abandoned, CCI can accept your build script. Take a look at [Bzip2](https://github.com/conan-io/conan-center-index/blob/master/recipes/bzip2/all/CMakeLists.txt) and [DirectShowBaseClasses](https://github.com/conan-io/conan-center-index/blob/master/recipes/directshowbaseclasses/all/CMakeLists.txt) as examples.

### System Packages

> :information_source: For exceptional cases where only system packages can be used and a regular Conan package may result in an incompatible and fragile package, a separated system package may be created. See the [FAQs](faqs.md#can-i-install-packages-from-the-system-package-manager) for more.

The [SystemPackageTool](https://docs.conan.io/en/latest/reference/conanfile/methods.html#systempackagetool) can easily manage a system package manager (e.g. apt,
pacman, brew, choco) and install packages which are missing on Conan Center but available for most distributions. It is key to correctly fill in the `cpp_info` for the consumers of a system package to have access to whatever was installed.

As example there are [glu](https://github.com/conan-io/conan-center-index/blob/master/recipes/glu/all/conanfile.py) and [OpenGL](https://github.com/conan-io/conan-center-index/blob/master/recipes/opengl/all/conanfile.py). Also, it will require an exception rule for [conan-center hook](https://github.com/conan-io/hooks#conan-center), a [pull request](https://github.com/conan-io/hooks/pulls) should be open to allow it over the KB-H032.

### Verifying Dependency Version

Some project requirements need to respect a version constraint. This can be enforced in a recipe by accessing the [`deps_cpp_info`](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#deps-cpp-info) attribute.
An exaple of this can be found in the [spdlog recipe](https://github.com/conan-io/conan-center-index/blob/9618f31c4d9b4da5d06f905befe9691cf105a1fc/recipes/spdlog/all/conanfile.py#L92-L94).

```py
if tools.Version(self.deps_cpp_info["liba"].version) < "7":
    raise ConanInvalidConfiguration(f"The project {self.name}/{self.version} requires liba > 7.x")
```

In Conan version 1.x this needs to be done in the `build` method, in future release is should be done in the `validate` method.

### Verifying Dependency Options

Certain projects are dependant on the configuration (a.k.a options) of a dependency. This can be enforced in a recipe by accessing the [`options`](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#options) attribute.
An example of this can be found in the [kealib recipe](https://github.com/conan-io/conan-center-index/blob/9618f31c4d9b4da5d06f905befe9691cf105a1fc/recipes/kealib/all/conanfile.py#L44-L46).

```py
    def validate(self):
        if not self.options["liba"].enable_feature:
            raise ConanInvalidConfiguration(f"The project {self.name}/{self.version} requires liba.enable_feature=True.")
```

## Test the recipe locally

The system will use the [conan-center hook](https://github.com/conan-io/hooks) to perform some quality checks. You can install the hook running:

```sh
conan config install https://github.com/conan-io/hooks.git -sf hooks -tf hooks
conan config set hooks.conan-center
```

The hook will show error messages but the `conan create` won’t fail unless you export the environment variable `CONAN_HOOK_ERROR_LEVEL=40`.
All hook checks will print a similar message:

```
[HOOK - conan-center.py] post_source(): [LIBCXX MANAGEMENT (KB-H011)] OK
[HOOK - conan-center.py] post_package(): ERROR: [PACKAGE LICENSE] No package licenses found
```

Call `conan create . lib/1.0@` in the folder of the recipe using the profile you want to test. For instance:

```sh
cd conan-center-index/recipes/boost/all
conan create conanfile.py boost/1.77.0@
```

### Updating conan hooks on your machine

The hooks are updated from time to time, so it's worth keeping your own copy of the hooks updated regularly. To do this:

```sh
conan config install
```

## Debugging failed builds

Go to the [Error Knowledge Base](error_knowledge_base.md) page to know more about Conan Center hook errors.

Some common errors related to Conan can be found on [troubleshooting](https://docs.conan.io/en/latest/faq/troubleshooting.html) section.

To test with the same enviroment, the [build images](supported_platforms_and_configurations.md#build-images) are available.
