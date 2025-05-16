# Developing Recipes Locally

Before you can contribute any code changes, you'll need to make sure you are familiar with the Conan client and have an environment that is conducive to developing recipes.

This file is intended to provide all the commands you need to run in order to be an expert ConanCenterIndex contributor.

<!-- toc -->
## Contents

  * [Clone your fork](#clone-your-fork)
  * [Basic Commands](#basic-commands)
    * [Try it yourself](#try-it-yourself)
  * [Debugging Failed Builds](#debugging-failed-builds)
  * [Running the Python Linters](#running-the-python-linters)
  * [Running the YAML Linters](#running-the-yaml-linters)
    * [Yamllint](#yamllint)
    * [Yamlschema](#yamlschema)
  * [Testing the different `test__package`](#testing-the-different-test__package)
  * [Testing more environments](#testing-more-environments)
      * [Docker build images used by ConanCenterIndex](#docker-build-images-used-by-conancenterindex)<!-- endToc -->

## Clone your fork

1. Follow the GitHub UI to [fork this repository](https://github.com/conan-io/conan-center-index/fork)
2. [Clone your fork](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)

## Basic Commands

We recommend working from the `recipes/project` folder itself. You can learn about the [recipe file structure](adding_packages/README.md#recipe-files-structure) to understand the folder and files located there.

> **Note**: You can only change one recipe per pull request, and working from the [_recipe folder_](adding_packages/README.md#the-recipe-folder-conanfilepy) will help prevent making a few mistakes. The default for this folder is `all`, follow the link above to learn more.

The [entire workflow of a recipe](https://docs.conan.io/2/tutorial/creating_packages.html) can be executed with the [`conan create`](https://docs.conan.io/2/reference/commands/create.html). This should look like:

* `conan create all/conanfile.py --version=0.1.0`

### Try it yourself

For instance you can create packages for `fmt` in various supported configurations by running:

```sh
cd recipes/fmt
conan create all/conanfile.py --version=9.0.0
conan create all/conanfile.py --version=9.0.0 -o "&:header_only=True"
conan create all/conanfile.py --version=9.0.0 -s build_type=Debug -o "*/*:shared=True"
```

## Debugging Failed Builds

Some common errors related to Conan can be found on [troubleshooting](https://docs.conan.io/2/knowledge/faq.html#troubleshooting) section.

Instructions for using these images can be found in [Testing more environments](#testing-more-environments) section.

In ConanCenterIndex, the most common failure point is upstream build scripts tailored to their specific use cases.
It's not uncommon to [patch build scripts](adding_packages/sources_and_patches.md#rules) but make sure to read the
[patch policy](adding_packages/sources_and_patches.md#policy-about-patching). You are encouraged first to submit pull requests upstream.


## Testing

This can be selected when calling `conan create` or separately with `conan test`

```sh
# Passing test package's conanfile directly (make sure to export first)
conan test recipes/fmt/all/test_package/conanfile.py fmt/9.0.0
```

## Testing more environments

This can be difficult for some platforms given virtualization support.

For Windows and MacOS users, you can test the Linux build environments with the Docker build images.

Assuming you've already tested it locally and it's been successfully exported to your cache, you can:

1. Creating a new profile.
   * You can also download them from CCI build summary
2. Build missing packages

Please, read [how to create Conan package using a Docker runner](https://docs.conan.io/2/examples/runners/docker/basic.html).

> **Note**: If you are running on Mac M1, the follow Docker argument is required: `--platform=linux/amd64`

If you are working with packages that have system dependencies that are managed by Conan

#### Docker build images used by ConanCenterIndex

The Conan Center Index uses [Conan Docker Tools](https://github.com/conan-io/conan-docker-tools/) to build packages in a variety of environments. All images are hosted in [Docker Hub](https://hub.docker.com/u/conanio).