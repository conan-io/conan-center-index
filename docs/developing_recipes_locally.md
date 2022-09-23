# Developing Recipes Locally

One of the early steps for contributing get getting familiar with the Conan client. There's also a few steps you need to take to get your environment setup.

This file is intended to provide all the commands you need to run in order to be an expert ConanCenter contributor.

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
  * [Testing the different `test__package`](#testing-the-different-test__package)
  * [Testing more environments](#testing-more-environments)
  * [Using Conan 2.0](#using-conan-20)<!-- endToc -->

## Clone your fork

1. Follow the GitHub UI to [fork this repository](https://github.com/conan-io/conan-center-index/fork)
2. [Clone your fork](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)

## Setup your environment

1. Install a C++ development toolchain - ConanCenter's [build images](#testing-more-environments) are available
2. [Install the Conan client](https://docs.conan.io/en/latest/installation.html) - make sure to keep it up to date!
3. Install CMake - this is the only tool which is assumed to be present
   [see FAQ](faqs.md#why-recipes-that-use-build-tools-like-cmake-that-have-packages-in-conan-center-do-not-use-it-as-a-build-require-by-default)

### Installing the ConanCenter Hooks

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

#### Updating conan hooks on your machine

The hooks are updated from time to time, so it's worth keeping your own copy of the hooks updated regularly. To do this:

```sh
conan config install
```

## Basic Commands

We recommend working from the `recipes/project` folder itself. You can learn about the [recipe file structure](how_to_add_packages.md#recipe-files-structure) to understand the folder and files located there.

> **Note**: You can only change one recipe per pull request, and working from the [_recipe folder_](hhow_to_add_packages.md#the-recipe-folder-conanfilepy) will help prevent making a few mistakes. The default for this folder is `all`, follow the link above to learn more.

The [entire workflow of a recipe](https://docs.conan.io/en/latest/developing_packages/package_dev_flow.html) can be execute with the [`conan create`](https://docs.conan.io/en/latest/reference/commands/creator/create.html). This should look like:

* `conan create all/conanfile.py 0.0.0@ -pr:b=default -pr:h=default`

ConanCenter also has a few [support settings/options](supported_platforms_and_configurations.md) which highly recommend to test. For example
`conan create all/conanfile.py 0.0.0@ -o project:shared=True -s build_type=Debug` is a easy way to more sure the package is correct.

### Try it yourself

For instance you can create packages for `fmt` in various supported configurations by running:

```sh
cd recipes/fmt
conan create all/conanfile.py fmt/9.0.0@ -pr:b=default -pr:h=default
conan create all/conanfile.py fmt/9.0.0@ -o fmt:header_only=True -pr:b=default -pr:h=default
conan create all/conanfile.py fmt/9.0.0@ -s build_type=Debug -o fmt:shared=True -pr:b=default -pr:h=default
```

## Debugging Failed Builds

Some common errors related to Conan can be found on [troubleshooting](https://docs.conan.io/en/latest/faq/troubleshooting.html) section.
For ConanCenter Hook errors, go to the [Error Knowledge Base](error_knowledge_base.md) page to know more about those.

To test with the same environment, the [build images](supported_platforms_and_configurations.md#build-images) are available.
Instructions for using these images can be found in [Testing more environments](#testing-more-environments)

## Running the Python Linters

Linters are always executed by Github actions to validate parts of your recipe, for instance, if it uses migrated Conan tools imports.
To understand how to run linters locally, read [V2 linter](v2_linter.md) documentation.

It is possible to run the linter locally the same way it is being run [using Github actions](../.github/workflows/linter-conan-v2.yml):

 * (Recommended) Use a dedicated Python virtualenv.
 * Ensure you have required tools installed: `conan` and `pylint` (better to uses fixed versions)

   ```
   pip install conan~=1.0 pylint==2.14
   ```

 * Set environment variable `PYTHONPATH` to the root of the repository

   ```
   export PYTHONPATH=your/path/conan-center-index
   ```

  * Now you just need to execute the `pylint` commands:

    ```
    # Lint a recipe:
    pylint --rcfile=linter/pylintrc_recipe recipes/boost/all/conanfile.py

    # Lint the test_package
    pylint --rcfile=linter/pylintrc_testpackage recipes/boost/all/test_package/conanfile.py
    ```

## Testing the different `test_*_package`

This can be selected when calling `conan create` or sperately with `conan test`

```sh
conan create recipes/fmt/all/conanfile.py 9.0.0@ -tf test_v1_package/ -pr:b=default -pr:h=default
```

```sh
conan test recipes/fmt/all/test_v1_package/conanfile.py fmt/9.0.0@ -pr:h=default -pr:b=default
```

## Testing more environments

This can be difficult for some platforms given virtualization support.

For Windows and MacOS users, you can test the Linux build environments by with the the Docker build images.

Assuming you've already tested it locally, and it's successfully export to your cache, you can:

1. Creating a new profile.
2. Build missing packages

Example.

```
docker run -v/Users/barbarian/.conan:/home/conan/.conan conanio/gcc8 bash -c "conan profile new --detect gcc8"
docker run -v/Users/barbarian/.conan:/home/conan/.conan conanio/gcc8 bash -c "conan install -pr gcc8 fmt/9.0.0@ --build missing"
```

> **Note**: If you are running on Mac M1, the follow Docker argument is required: `--platform=linux/amd64

## Using Conan 2.0

Everything you need to know about the methods, commands line, outputs can be found in the
[Conan 2.0 Migrations](https://docs.conan.io/en/latest/conan_v2.html) docs. This should be fairly straight forward.
Conan 2.0 by default has a different `CONAN_USER_HOME` location. You can have to separate caches, profiles
and settings. So no need to worry about breaking your v1 setup.

> **Note**: There are pretty heavy changes to the CLI so very few of the commands will have survived.
> [Unified Command Pattern](https://docs.conan.io/en/latest/migrating_to_2.0/commands.html#unified-patterns-in-command-arguments)
> for example changes how settings and options are passed.


Simply install Conan with `pip install conan --upgrade --pre`

You can confirm the installation with

```sh
$ conan --version
Conan version 2.0.0-beta2
$ conan config home
Current Conan home: /Users/barbarian/.conan2
```

> **Note**: You will most likely see
> ```
> Initialized file: '/Users/christopherm/.conan2/settings.yml'
> Initialized file: '/Users/christopherm/.conan2/extensions/plugins/compatibility/compatibility.py'
> Initialized file: '/Users/christopherm/.conan2/extensions/plugins/compatibility/app_compat.py'
> Initialized file: '/Users/christopherm/.conan2/extensions/plugins/compatibility/cppstd_compat.py'
> Initialized file: '/Users/christopherm/.conan2/extensions/plugins/profile.py'
> ```
> When running the client for the first time.

You will need to setup profiles

```sh
conan profile detect
```

> **Warning**: This is a best guess, you need to make sure it's correct.

There is a remote for the 2.0 migration binaries which can be added

```
conan remote add conanv2 https://conanv2beta.jfrog.io/artifactory/api/conan/conan --index 0
```

Trying build an existing recipe

```sh
cd recipes/fmt
conan create all/conanfile.py --version 9.0.0
conan create all/conanfile.py --version 9.0.0 -o fmt/9.0.0:header_only=True
conan create all/conanfile.py --version 9.0.0 -s build_type=Debug -o fmt/9.0.0:shared=True
```
