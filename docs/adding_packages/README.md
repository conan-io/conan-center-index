# Adding Packages to ConanCenter

ConanCenterIndex aims to provide the best quality packages of any open source project.
Any C/C++ project can be made available by contributing a "recipe".

Getting started is easy. Try building an existing package with our [developing recipes](../developing_recipes_locally.md) tutorial.
To deepen you understanding, start with the [How to provide a good recipe](#how-to-provide-a-good-recipe) section.
You can follow the three steps (:one: :two: :three:) described below! :tada:

<!-- toc -->
## Contents

  * [:one: Request access](#one-request-access)
  * [:two: Creating a package](#two-creating-a-package)
    * [How to provide a good recipe](#how-to-provide-a-good-recipe)
  * [:three: Submitting a Package](#three-submitting-a-package)
  * [The Build Service](#the-build-service)<!-- endToc -->

## :one: Request access

The first step to add packages to ConanCenter is requesting access. To enroll in ConanCenter repository, please write a comment
requesting access in this GitHub [issue](https://github.com/conan-io/conan-center-index/issues/4). Feel free to introduce yourself and
your motivation to join ConanCenter community.

This process helps ConanCenter against spam and malicious code. The process is not not automated on purpose and the requests are generally approved
on a weekly basis.

> **Note** The requests are reviewed manually, checking the GitHub profile activity of the requester to avoid any misuse of the service.
> All interactions are subject to the expectations of the [code of conduct](../code_of_conduct.md). Any misuse or inappropriate behavior are subject
> to the same principals.

When submitting a pull request for the first time, you will be prompted to sign the [CLA](../CONTRIBUTOR_LICENSE_AGREEMENT.md) for your code contributions. You can view your signed CLA's by going to <https://cla-assistant.io/> and signing in.

### Inactivity and user removal

For security reasons related to the CI, when a user no longer contributes for a long period, it will be considered inactive and removed from the authorized user's list.
For now, it's configured for **4 months**, and it's computed based on the latest commit, not comments or opened issues.
After that time, the CI bot will ask to remove the user name from the authorized users' list through the access request PR, which occurs a few times every week.
In case you are interested in coming back, please, ask again to be included in the issue [#4](https://github.com/conan-io/conan-center-index/issues/4), the process will be precise like for newcomers.

## :two: Creating a package

Once you've successfully built an existing recipe following [developing recipes](../developing_recipes_locally.md) tutorial.
You are set to being.

Make sure you have:

* Fork and then clone the [conan-center-index](https://github.com/conan-io/conan-center-index/fork) git repository.
* Make sure you are using the latest [Conan client](https://conan.io/downloads) version, as recipes might evolve introducing features of the newer Conan releases.

The easiest way is to copy a template from [package_templates](../package_templates) folder in the recipes/ folder and rename it to the project name (it should be lower-case). Read templates [documentation](../package_templates/README.md) to find more information.

Quickly, there's a few items to look at:

* Rename the folder and recipe - names are always lowercase
* Add _only_ the latest version in the [`config.yml`](folders_and_files.md#configyml) and [`conandata.yml`](folders_and_files.md#conandatayml)
* Make sure to update the [`ConanFile` attributes](conanfile_attributes.md) like `license`, `description`, ect...

In ConanCenter, our belief is recipes should always match upstream, in other words, what the original author(s) intended.

* Options should [follow the recommendations](conanfile_attributes.md#options) as well as match the default of upstream.
* [Package information](build_and_package.md), libraries, components should match as well. This includes exposing supported build system names.

Where dependencies are involved, there's no shortcuts, inspect the upstream's build scripts for how they usually consume them. Pick the Conan
generator that matches. The most common example is CMake's `find_package` can be satisfied by Conan's `CMakeDeps` generator. There are a few
things to be cautious about, many projects like to "vendor" other projects within them. This can be files checked into the repository or
downloaded during the build process.

### How to provide a good recipe

Take a look at existing [recipes](https://github.com/conan-io/conan-center-index/tree/master/recipes) available in CCI can be used as good examples,
you can use them as the base for your recipe. The GitHub search is very good for matching code snippets, you can see if, how or when a function
is used in other recipes.

> **Note**: Conan features change over time and our best practices evolve so some minor details may be out of date due to the vast number of recipes.

More often then not, ConanCenter recipes are built in more configuration then the upstream project - this means some edge cases need minor tweaks.
We **strongly encourage** everyone to contribute back to the upstream project. This reduce the burden of reapplying patches and overall makes the
the code more accessible.

Read the docs! The [FAQs](../faqs.md) are a great place to find short answers.
The documents in this folder are written to explain each folder, file, method and attribute with specific conventions

1. [Folders and Files](folders_and_files.md)
2. [Sources and Patches](sources_and_patches.md)
   1. [`conandata.yml` format](conandata_yml_format.md)
3. [`ConanFile` Attributes](conanfile_attributes.md)
4. [Requirements](dependencies_and_requirements.md)
5. [Build and Package](build_and_package.md)
   1. [Revisit Patches](sources_and_patches.md#policy-about-patching)
6. [Test Package](test_packages.md)

The one place you are certain to find a lot of information is <https://docs.conan.io>, this has the documentation for everything in Conan.
There are helpful tutorials for cross-build, detailed explication for profiles and settings and much much more!

## :three: Submitting a Package

To contribute a package, you can submit a [Pull Request](https://github.com/conan-io/conan-center-index/pulls) to this GitHub
repository <https://github.com/conan-io/conan-center-index>.

The specific steps to submitting changes are:

* Build and test the new recipe in several combinations. Check [developing recipes](../developing_recipes_locally.md) for tips.
* [Commit and push to your fork repository](https://docs.github.com/en/get-started/using-git/pushing-commits-to-a-remote-repository) then
  [submit a pull request](https://github.com/conan-io/conan-center-index/compare).
* Our automated [build service](#the-build-service) will build 100+ different configurations, and provide messages that indicate if there
  were any issues found during the pull request on GitHub.

When the pull request is [reviewed and merged](../review_process.md), those packages are published to [JFrog's ConanCenter](https://conan.io/center/) and available for everyone.

## The Build Service

The **build service** associated to this repo will generate binary packages automatically for the most common platforms and compilers. See [the Supported Platforms and Configurations page](../supported_platforms_and_configurations.md) for a list of generated configurations. For a C++ library, the system is currently generating more than 100 binary packages.

> **Note**: This not a testing service, it is a binary building service for package **released**. Unit tests shouldn't be built nor run in recipes by default, see the [FAQs](../faqs.md#why-conancenter-does-not-build-and-execute-tests-in-recipes) for more. Before submitting a pull request, please ensure that it works locally for some configurations.

* The CI bot will start a new build only [after the author is approved](#one-request-access). Your PR may be reviewed in the mean time, but is not guaranteed.
* The CI system will also report with messages in the PR any error in the process, even linking to the logs to see more details and debug.
* The Actions are used to lint and ensure the latest conventions are being used. You'll see comments from bots letting you know.

The pipeline will report errors and build logs by creating a comment in the pull-request after every commit. The message will include links to the logs for inspecting.

Packages generated and uploaded by this build service does not include any _user_ or _channel_ (existing references with any `@user/channel` should be considered as deprecated in favor of packages without it). Once the packages are uploaded, you will be able to install them using the reference as `name/version` (requires Conan >= 1.21): `conan install cmake/3.18.2@`.
