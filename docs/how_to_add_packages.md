# Adding Packages to ConanCenter

The [conan-center-index](https://github.com/conan-io/conan-center-index) (this repository) contains recipes for the remote [JFrog ConanCenter](https://conan.io/center/).
This remote is added by default to a clean installation of the Conan client. Recipes are contributed by opening pull requests as explained in the sections below.
When pull requests are merged, the CI will upload the generated packages to the [conancenter](https://conan.io/center/) remote.

<!-- toc -->
## Contents

  * [Request access](#request-access)
  * [Submitting a Package](#submitting-a-package)
    * [The Build Service](#the-build-service)
  * [More Information about Recipes](#more-information-about-recipes)
    * [The recipe folder](#the-recipe-folder)
    * [The version folder(s)](#the-version-folders)
    * [The `conanfile.py` and `test_package` folder](#the-conanfilepy-and-test_package-folder)
    * [The `conandata.yml`](#the-conandatayml)
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

:one: The first step in adding packages to ConanCenter is requesting access. To enroll in ConanCenter repository, please write a comment
requesting access in this GitHub [issue](https://github.com/conan-io/conan-center-index/issues/4). Feel free to introduce yourself and
your motivation to join ConanCenter.

All requests are reviewed and approved every week, please be patient, the process is not automated and it won't be. This
process helps conan-center-index against spam and malicious code.

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

## More Information about Recipes

### The recipe folder

Create a new subfolder in the [recipes](https://github.com/conan-io/conan-center-index/tree/master/recipes) folder with the name of the package in lowercase.

e.g:

```
.
+-- recipes
|   +-- zlib
|       +-- 1.2.8
|           +-- conanfile.py
|           +-- test_package/
|       +-- 1.2.11
|           +-- conanfile.py
|           +-- test_package/
```

### The version folder(s)

The system supports to use the same recipe for several versions of the library and also to create different recipes for different versions

- **1 version => 1 recipe**

  When the recipe changes significantly between different library versions and reusing the recipe is not worth it, it is recommended to create different folders and group together the
  versions that can share the same recipe. Each of these folders will require its own `conanfile.py` and `test_package` folder:

  ```
  .
  +-- recipes
  |   +-- zlib
  |       +-- 1.2.8
  |           +-- conanfile.py
  |           +-- test_package/

  ```


- **N versions => 1 recipe**

   Create a folder named `all` (just a convention) and put both the `conanfile.py` and the `test_package` folder there.

   You will need to create a `config.yml` file to declare the matching between the versions and the folders. e.g:

  ```
  .
  +-- recipes
  |   +-- mylibrary
  |       +-- all
  |           +-- conanfile.py
  |           +-- test_package/
          +-- config.yml
  ```

  **config.yml** file

  ```yml
  versions:
    "1.1.0":
      folder: all
    "1.1.1":
      folder: all
    "1.1.2":
      folder: all
  ```

- **N versions => M recipes**

   This is the same approach as the previous one, you can use one recipe for a range of versions and a different one for another range of versions. Create the `config.yml` file and declare the folder for each version.

### The `conanfile.py` and `test_package` folder

In the folder(s) created in the previous step, you have to create the `conanfile.py` and a [`test_package`](https://docs.conan.io/en/latest/creating_packages/getting_started.html#the-test-package-folder) folder.

### The `conandata.yml`

In the same directory as the `conanfile.py`, create a file named `conandata.yml`. This file has to be used in the recipe to indicate the origins of the source code.
It must have an entry for each version, indicating the URL for downloading the source code and a checksum.

```yml
sources:
  "1.1.0":
    url: "https://www.url.org/source/mylib-1.0.0.tar.gz"
    sha256: "8c48baf3babe0d505d16cfc0cf272589c66d3624264098213db0fb00034728e9"
  "1.1.1":
    url: "https://www.url.org/source/mylib-1.0.1.tar.gz"
    sha256: "15b6393c20030aab02c8e2fe0243cb1d1d18062f6c095d67bca91871dc7f324a"
```

You must specify the checksum algorithm `sha256`.
If your sources are on GitHub, you can copy the link of the "Download ZIP" located in the "Clone or download" repository, make sure you are in the correct branch or TAG.

Then in your `conanfile.py` method, it has to be used to download the sources:

```py
 def source(self):
     tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)
```

> :warning: Please be aware that `conan-center-index` only builds from sources and pre-compiled binaries are not acceptable. For more information see our [packaging policy](packaging_policy.md).

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

> :information_source: For exceptional cases where only system packages can be used and a regular Conan package may result in an incompatible and fragile package, a separated system package may be created. See the [FAQs](https://github.com/conan-io/conan-center-index/blob/master/docs/faqs.md#can-i-install-packages-from-the-system-package-manager) for more.
 
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
