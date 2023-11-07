# Developing Recipes Locally

Before you can contribute any code changes, you'll need to make sure you are familiar with the Conan client and have an environment that is conducive to developing recipes.

This file is intended to provide all the commands you need to run in order to be an expert ConanCenterIndex contributor.

> **Note**: If you are working with Conan 2.0, the [instructions are below](#using-conan-20)

<!-- toc -->
## Contents

  * [Clone your fork](#clone-your-fork)
  * [Setup your environment](#setup-your-environment)
    * [Installing the ConanCenter Hooks](#installing-the-conancenter-hooks)
      * [Updating conan hooks on your machine](#updating-conan-hooks-on-your-machine)
  * [Basic Commands](#basic-commands)
    * [Try it yourself](#try-it-yourself)
  * [Debugging Failed Builds](#debugging-failed-builds)
  * [Running the Python Linters](#running-the-python-linters)
  * [Running the YAML Linters](#running-the-yaml-linters)
    * [Yamllint](#yamllint)
    * [Yamlschema](#yamlschema)
  * [Testing the different `test__package`](#testing-the-different-test__package)
  * [Testing more environments](#testing-more-environments)
      * [Docker build images used by ConanCenterIndex](#docker-build-images-used-by-conancenterindex)
  * [Using Conan 2.0](#using-conan-20)
    * [Installing Conan 2.0 beta](#installing-conan-20-beta)
    * [Trying it out](#trying-it-out)<!-- endToc -->

## Clone your fork

1. Follow the GitHub UI to [fork this repository](https://github.com/conan-io/conan-center-index/fork)
2. [Clone your fork](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)

## Setup your environment

1. Install a C++ development toolchain - ConanCenter's [build images](#testing-more-environments) are available
2. [Install the Conan client](https://docs.conan.io/1/installation.html) - make sure to keep it up to date!
3. Install CMake - this is the only tool which is assumed to be present
   [see FAQ](faqs.md#why-recipes-that-use-build-tools-like-cmake-that-have-packages-in-conan-center-do-not-use-it-as-a-build-require-by-default) for details.

> **Note**: It's recommended to use a dedicated Python virtualenv when installing with `pip`.

### Installing the ConanCenter Hooks

> **Warning**: This is not yet supported with Conan 2.0. Please, follow the instructions below only in case you are using Conan 1.0.

The system will use the [conan-center hooks](https://github.com/conan-io/hooks) to perform some quality checks. You can install the hooks by running:

```sh
conan config install https://github.com/conan-io/hooks.git -sf hooks -tf hooks
conan config set hooks.conan-center
```

> **Note**: Hooks are generally for package correctness and the pylinters are for the recipe syntax

The hooks will show error messages but the `conan create` won’t fail unless you export the environment variable `CONAN_HOOK_ERROR_LEVEL=40`.
All hooks checks will print a similar message:

```txt
[HOOK - conan-center.py] post_source(): [LIBCXX MANAGEMENT (KB-H011)] OK
[HOOK - conan-center.py] post_package(): ERROR: [PACKAGE LICENSE] No package licenses found
```

#### Updating conan hooks on your machine

The hooks are updated from time to time, so it's worth keeping your own copy of the hooks updated regularly. To do this, simply run:

```sh
conan config install
```

## Basic Commands

We recommend working from the `recipes/project` folder itself. You can learn about the [recipe file structure](adding_packages/README.md#recipe-files-structure) to understand the folder and files located there.

> **Note**: You can only change one recipe per pull request, and working from the [_recipe folder_](adding_packages/README.md#the-recipe-folder-conanfilepy) will help prevent making a few mistakes. The default for this folder is `all`, follow the link above to learn more.

The [entire workflow of a recipe](https://docs.conan.io/1/developing_packages/package_dev_flow.html) can be execute with the [`conan create`](https://docs.conan.io/1/reference/commands/creator/create.html). This should look like:

* `conan create all/conanfile.py 0.0.0@ -pr:b=default -pr:h=default`

ConanCenter also has a few [support settings and options](supported_platforms_and_configurations.md) which highly recommend to test. For example
`conan create all/conanfile.py 0.0.0@ -o project:shared=True -s build_type=Debug` is a easy way to test more configurations ensuring the package is correct.

### Try it yourself

For instance you can create packages for `fmt` in various supported configurations by running:

```sh
cd recipes/fmt
conan create all/conanfile.py fmt/9.0.0@ -pr:b=default -pr:h=default
conan create all/conanfile.py fmt/9.0.0@ -o fmt:header_only=True -pr:b=default -pr:h=default
conan create all/conanfile.py fmt/9.0.0@ -s build_type=Debug -o fmt:shared=True -pr:b=default -pr:h=default
```

## Debugging Failed Builds

Some common errors related to Conan can be found on [troubleshooting](https://docs.conan.io/1/faq/troubleshooting.html) section.
For ConanCenter Hook errors, go to the [Error Knowledge Base](error_knowledge_base.md) page to know more about those.

To test with the same environment, the [build images](supported_platforms_and_configurations.md#build-images) are available.
Instructions for using these images can be found in [Testing more environments](#testing-more-environments) section.

In ConanCenterIndex, the most common failure point is upstream build scripts tailored to their specific use cases.
It's not uncommon to [patch build scripts](adding_packages/sources_and_patches.md#rules) but make sure to read the
[patch policy](adding_packages/sources_and_patches.md#policy-about-patching). You are encouraged to submit pull requests upstream.

## Running the Python Linters

> **Warning**: This is not yet supported with Conan 2.0

Linters are always executed by GitHub Actions to validate parts of your recipe, for instance, if it uses migrated Conan tools imports.

It is possible to run the linter locally the same way it is being run [using Github actions](../.github/workflows/linter-conan-v2.yml) by:

* (Recommended) Use a dedicated Python virtualenv.
* Ensure you have required tools installed: `conan` and `pylint` (better to uses fixed versions)

  ```sh
  pip install conan~=1.0 pylint==2.14
  ```

* Set environment variable `PYTHONPATH` to the root of the repository

  ```sh
  export PYTHONPATH=your/path/conan-center-index
  ```

* Now you just need to execute the `pylint` commands:

  ```sh
  # Lint a recipe:
  pylint --rcfile=linter/pylintrc_recipe recipes/fmt/all/conanfile.py

  # Lint the test_package
  pylint --rcfile=linter/pylintrc_testpackage recipes/fmt/all/test_package/conanfile.py
  ```

## Running the YAML Linters

There's two levels of YAML validation, first is syntax and the second is schema.
The style rules are located in [`linter/yamllint_rules.yml`](../linter/yamllint_rules.yml) and are used to ensure consistence.
The [`config.yml`](adding_packages/README.md#configyml) is required for the build infrastructure and the
[`conandata.yml` patch fields](adding_packages/conandata_yml_format.md#patches-fields) have required elements that are enforced with
schema validation. There's are to encourage the best possible quality of recipes and make reviewing faster.

### Yamllint

* (Recommended) Use a dedicated Python virtualenv.
* Ensure you have required tools installed: `yamllint` (better to uses fixed versions)

  ```sh
  pip install yamllint==1.28
  ```

* Now you just need to execute the `yamllint` commands:

  ```sh
  # Lint a recipe:
  yamllint --config-file linter/yamllint_rules.yml -f standard recipes/config.yml
  yamllint --config-file linter/yamllint_rules.yml -f standard recipes/fmt/all/conandata.yml
  ```

### Yamlschema

* (Recommended) Use a dedicated Python virtualenv.
* Ensure you have required tools installed: `strictyaml` and `argparse` (better to uses fixed versions)

  ```sh
  pip install strictyaml==1.16 argparse==1.4
  ```

* Now you just need to execute the validation scripts:

  ```sh
  # Lint a config.yml:
  python3 linter/config_yaml_linter.py recipes/fmt/config.yml

  # Lint a conandata.yml
  python3 linter/conandata_yaml_linter.py recipes/fmt/all/conandata.yml
  ```

## Testing the different `test_*_package`

This can be selected when calling `conan create` or separately with `conan test`

```sh
# By adding the `-tf` argument
conan create recipes/fmt/all/conanfile.py 9.0.0@ -tf test_v1_package/ -pr:b=default -pr:h=default
```

```sh
# Passing test package's conanfile directly (make sure to export first)
conan test recipes/fmt/all/test_v1_package/conanfile.py fmt/9.0.0@ -pr:h=default -pr:b=default
```

## Testing more environments

This can be difficult for some platforms given virtualization support.

For Windows and MacOS users, you can test the Linux build environments with the Docker build images.

Assuming you've already tested it locally and it's been successfully exported to your cache, you can:

1. Creating a new profile.
   * You can also download them from CCI build summary
2. Build missing packages

Example.

```sh
docker run -v/Users/barbarian/.conan:/home/conan/.conan conanio/gcc8 bash -c "conan profile new --detect gcc8"
docker run -v/Users/barbarian/.conan:/home/conan/.conan conanio/gcc8 bash -c "conan install -pr gcc8 fmt/9.0.0@ --build missing"
```

> **Note**: If you are running on Mac M1, the follow Docker argument is required: `--platform=linux/amd64`

If you are working with packages that have system dependencies that are managed by Conan

```sh
docker run -e CONAN_SYSREQUIRES_MODE=enabled conanio/gcc11-ubuntu16.04 conan install fmt/9.0.0@ -if build --build missing -c tools.system.package_manager:mode=install -c tools.system.package_manager:sudo=yes
```

#### Docker build images used by ConanCenterIndex

The Conan Center Index uses [Conan Docker Tools](https://github.com/conan-io/conan-docker-tools/) to build packages in a variety of environments. All images are hosted in [Docker Hub](https://hub.docker.com/u/conanio). The relation of the images with the build configurations is available according to the Conan configuration, as `node_labels.Linux`, for instance:


```yaml
node_labels:
  Linux:
    x86_64:
      "gcc":
        default: "linux_gcc_${compiler.version}"
        "11": "linux_gcc_${compiler.version}_ubuntu16.04"
      "clang":
        default: "linux_clang_${compiler.version}_ubuntu16.04"
        "11": "linux_clang_${compiler.version}"
```

The configuration files are located in the folder [../.c3i](../.c3i). Currently are the files [config_v1.yml](../.c3i/config_v1.yml) and [config_v2.yml](../.c3i/config_v2.yml). The configuration file `config_v1.yml` is used by the Conan 1.0 client, while `config_v2.yml` is used by the Conan 2.0 client.

The label `linux` refers to any Docker image, while `gcc_${compiler.version}` refers to GCC + a compiler version. For example, `linux_gcc_10` refers to the image `conanio/gcc10`.
The suffix `_ubuntu16.04` refers to the base image used by the Docker image, in this case, `ubuntu16.04`. So, `"11": "linux_gcc_${compiler.version}_ubuntu16.04"` means that the image `conanio/gcc11-ubuntu16.04`. Thus, all GCC versions use `conanio/gcc<version>`, except for the GCC 11, which uses `conanio/gcc11-ubuntu16.04`. The same applies to Clang.


## Using Conan 2.0

Everything you need to know about the methods, commands line, outputs can be found in the
[Conan 2.0 Migrations](https://docs.conan.io/1/conan_v2.html) docs.

This should be non-intrusive. Conan 2.0 by default has a different `CONAN_USER_HOME` location, which means that it has separate caches, profiles, and settings.
This will leave your Conan 1.0 setup completely intact when using Conan 2.0.

> **Note**: There are substantial changes to the CLI so very few of the commands will remain the same.
> The new [Unified Command Pattern](https://docs.conan.io/1/migrating_to_2.0/commands.html#unified-patterns-in-command-arguments),
> as an example, changes how settings and options are passed.

### Installing Conan 2.0 beta

Simply install Conan 2.0 with `pip install conan --upgrade --pre`.

You can confirm the installation with:

```sh
$ conan --version
Conan version 2.0.0-beta3
$ conan config home
Current Conan home: /Users/barbarian/.conan2
```

> **Note**: You will most likely see
>
> ```sh
> Initialized file: '/Users/barbarian/.conan2/settings.yml'
> Initialized file: '/Users/barbarian/.conan2/extensions/plugins/compatibility/compatibility.py'
> Initialized file: '/Users/barbarian/.conan2/extensions/plugins/compatibility/app_compat.py'
> Initialized file: '/Users/barbarian/.conan2/extensions/plugins/compatibility/cppstd_compat.py'
> Initialized file: '/Users/barbarian/.conan2/extensions/plugins/profile.py'
> ```
>
> When running the client for the first time.

You will need to setup profiles. This is one of the changes in 2.0. The default profile is now opt-in and no longer generated automatically.

```sh
conan profile detect
```

> **Warning**: This is a best guess, you need to make sure it's correct.

### Trying it out

Try building an existing recipe. We'll repeat the 1.x example with `fmt` to build the same configurations:

```sh
cd recipes/fmt
conan create all/conanfile.py --version 9.0.0
conan create all/conanfile.py --version 9.0.0 -o fmt/9.0.0:header_only=True
conan create all/conanfile.py --version 9.0.0 -s build_type=Debug -o fmt/9.0.0:shared=True
```
