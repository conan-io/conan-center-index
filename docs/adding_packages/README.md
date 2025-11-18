# Adding Packages to ConanCenter

ConanCenterIndex aims to provide the best quality packages of any open source project.
Any C/C++ project can be made available by contributing a "recipe".

Getting started is easy. Try building an existing package with our [developing recipes](../developing_recipes_locally.md)
tutorial. To deepen you understanding, start with the [How to write a good recipe](#how-to-provide-a-good-recipe) section.
You can follow the three steps (:one: :two: :three:) described below! :tada:

<!-- toc -->
## Contents
  * [:one: First time contributors](#one-first-time-contributors)
  * [:two: Creating a package](#two-creating-a-package)
    * [How to write a good recipe](#how-to-provide-a-good-recipe)
  * [:three: Submitting a Package](#three-submitting-a-package)
  * [The Build Service](#the-build-service)<!-- endToc -->

## :one: First time contributors

When submitting a pull request for the first time, you will be prompted to sign the [CLA](https://cla-assistant.io/conan-io/conan-center-index) for your
code contributions. You can view your signed CLA's by going to <https://cla-assistant.io/> and signing in.

## :two: Creating a package

Once you've successfully built an existing recipe following [developing recipes](../developing_recipes_locally.md) tutorial.
You are set to being adding a new package.

Make sure you have:

* Forked and then cloned the [conan-center-index](https://github.com/conan-io/conan-center-index) git repository.
* Make sure you are using a recent [Conan client](https://conan.io/downloads) version, as recipes improve by introducing features of the newer Conan releases.

The easiest way to start is copying a template from our [`package_templates/`](../package_templates) folder to the [`recipes/`](../../recipes/) folder.
Rename the new folder following the [project name](conanfile_attributes.md#name) guidelines. Read templates [documentation](../package_templates/README.md)
to find more information.

Quickly, there's a few items to look at:

* Add _only_ the latest version in the [`config.yml`](folders_and_files.md#configyml) and [`conandata.yml`](folders_and_files.md#conandatayml)
* Make sure to update the [`ConanFile` attributes](conanfile_attributes.md) like `license`, `description`, etc...

In ConanCenter, our belief is recipes should always match upstream, in other words, what the original author(s) intended.

* Options should [follow these recommendations](conanfile_attributes.md#options) as well as match the default value used by the upstream project.
* [Package information](build_and_package.md), libraries, components should match as well. This includes exposing supported build system names.

### How to write a good recipe

Take a look at existing [recipes](https://github.com/conan-io/conan-center-index/tree/master/recipes) available in ConanCenterIndex which can be
used as good examples, you can use them as the base for your recipe. The GitHub search is very good for matching code snippets, you can see if,
how or when a function is used in other recipes.

> **Note**: Conan features change over time and our best practices evolve so some minor details may be out of date due to the vast number of recipes.

More often than not, ConanCenter recipes are built in more configuration than the upstream project. This means some edge cases need minor tweaks.
We **strongly encourage** everyone to contribute back to the upstream project. This reduces the burden of re-applying patches and overall makes the
the code more accessible.

Read the docs! The [FAQs](../faqs.md) are a great place to find short answers.
The documents in this folder are written to explain each folder, file, method, and attribute.

1. [Folders and Files](folders_and_files.md)
2. [Sources and Patches](sources_and_patches.md)
   1. [`conandata.yml` format](conandata_yml_format.md)
3. [`ConanFile` Attributes](conanfile_attributes.md)
4. [Dependencies](dependencies.md)
5. [Build and Package](build_and_package.md)
   1. [Revisit Patches](sources_and_patches.md#policy-about-patching)

The one place you are certain to find a lot of information is <https://docs.conan.io>, this has the documentation for everything in Conan.
There are helpful tutorials for cross-build, detailed explication for profiles and settings and much much more!

## :three: Submitting a Package

To contribute a package, you can submit a [Pull Request](https://github.com/conan-io/conan-center-index/pulls) to this GitHub
repository <https://github.com/conan-io/conan-center-index>.

The specific steps to submitting changes are:

* Build and test the new recipe in several combinations. Check [developing recipes](../developing_recipes_locally.md) for tips.
* [Commit and push to your fork repository](https://docs.github.com/en/get-started/using-git/pushing-commits-to-a-remote-repository) then
  [submit a pull request](https://github.com/conan-io/conan-center-index/compare).

When the pull request is [reviewed and merged](../review_process.md), those packages are published to [JFrog's ConanCenter](https://conan.io/center/)
and are made available for everyone.

## The Build Service

The **build service** associated to this repository will generate binary packages automatically for the most common platforms and compilers.
See [the Supported Platforms and Configurations page](../supported_platforms_and_configurations.md) for a list of generated configurations.
For a C++ library, the system is currently generating more than 30 binary packages.

> **Note**: This not a testing service, it is a binary building service for **released** packages. Unit tests shouldn't be built nor run in recipes by default, see the [FAQs](../faqs.md#why-conancenter-does-not-build-and-execute-tests-in-recipes) for more. Before submitting a pull request, please ensure that it works locally for some configurations.

- The CI system will report the build logs in the Checks tab, in the pull-request.
- Linter and Hooks are automatically displayed in the Checks tab as well.
