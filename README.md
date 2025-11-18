Conan Center Index (Entos)
==========================
![build and upload](https://github.com/entos-xe/conan-center-index/actions/workflows/build_and_upload.yml/badge.svg)


This is the Sky Entos-XE fork of the [conan center index]().
It is [recommended best practice](https://docs.conan.io/2/devops/conancenter/hosting_binaries.html) by Conan that
organizations fork their own copies of CCI to customize package versions and provide updates more
quickly than can be guaranteed by the PR review process in the public upstream repository
(which can often take many weeks).

Where possible, package updates should still be commited to the upstream repository as a PR.

Not all packages available in CCI will be provided by the
[Comcast Artifactory](https://partners.artifactory.comcast.com) instance, only those listed in the `entos-packages.yml` file.

### Branches

* `entos-master`: the default branch for this repository.
* `master`: the default branch for the upstream repository.
* `upstream-update`: The branch used to merge updates from the upstream repository.

### Updating or providing a new package:

1. Create a PR to update the repository.
2. Check first that the package and or version is not available from the upstream repository.
   If it is, pull the changes from upstream. Check also that a PR has not also been raised upstream,
   you may be able to use this.
3. If necessary, add or update the required package
4. Add the package and **and any dependencies** to `entos-packages.yml`

Upon a successful PR build, the package will be available from 
[conan-entos-iui-dev](https://partners.artifactory.comcast.com/ui/repos/tree/General/conan-entos-iui-dev) for testing.

When the PR is merged to `master`, the package recipe will be available from the main 
[conan-entos-iui-prod](https://partners.artifactory.comcast.com/ui/repos/tree/General/conan-entos-iui-prod)
repository.

### Updating from upstream

To merge updates from the upstream repository, create a new branch called `upstream-update`.
This branch name will be used to disable CI Workflow checks which normally only allow one
recipe to be updated at a time.

### CI Notes

* Only pushes to the `entos-master` branch upload packages to the `conan-entos-iui-prod` repository. Other branches
  push to the `conan-entos-iui-dev` repository.

* Only recipes (the python files) are uploaded. Binary packages should be built by the consuming application or library.

---

<p align="center">
    <img src="assets/JFrogConanCenter.png" width="600"/>
</p>

Conan Center Index is the source index of recipes of the [ConanCenter](https://conan.io/center) package repository for [Conan](https://conan.io).

This repository includes a Continuous Integration system that will build automatically the Conan packages for the recipes submitted via
[Pull Request](https://github.com/conan-io/conan-center-index/pulls).

### Server Status

The current Conan Center Index CI status can be found on https://status.conan.io/

Any maintenance, outage or important event related to the CI will be informed there.


### Configure the Conan Center remote

> [!IMPORTANT]
> The Conan Center remote URL changed for **Conan 2** on November 2024 - the new URL is the default on new installations of Conan since version 2.9.2.
>
> New recipe updates are only published to this remote and are only guaranteed to be compatible with recent versions of Conan 2.
>
> All previously published recipes and packages known to be compatible with Conan 2 are also served by this remote.

To update an existing Conan 2 installation:

```
conan remote update conancenter --url https://center2.conan.io
```

#### Conan Center legacy remote

The legacy remote at `https://center.conan.io` stopped receiving updates on 4 November 2024 and is frozen and will no longer received updates.
It is kept in this state to avoid breaking any existing Conan 1.x installations.


### How to consume recipes

Starting to use recipes from this repository is as easy as running
one simple command after installing Conan:

```
conan install --require=name/version [-g <generator>]
```

For further details, please see the [Conan documentation](https://docs.conan.io/2/tutorial/consuming_packages.html).

:warning: It is very important to notice that recipes will evolve over time
and, while they are fixing some issues, they might introduce new features and
improvements, and your project can break if you upgrade them
([How to prevent these breaking changes in my project?](docs/consuming_recipes.md)).



### Documentation

All the documentation is available in this same repository in the [`docs/` subfolder](docs/README.md).

This is a list of shortcuts to some interesting topics:

* :rocket: If you want to learn how to **contribute new recipes**, please read [docs/adding_packages/](docs/adding_packages/README.md).
* :speech_balloon: **FAQ**: most common questions are listed in [docs/faqs.md](docs/faqs.md).
* :hammer_and_wrench: The internal changes related to infrastructure can be checked in [docs/changelog.md](docs/changelog.md).
* :world_map: There are various community lead initiatives which are outlined in [docs/community_resources.md](docs/community_resources.md).

### Reporting Issues

You can open issues in the [issue tracker](https://github.com/conan-io/conan-center-index/issues) to:

* :bug: Report **bugs/issues** in a package:
    - Use the `[package]` tag in the title of the issue to help identifying them.
    - If you detect any issue or missing feature in a package, for example, a build failure or a recipe that not support a specific configuration.
    - Specify the name and version (`zlib/1.2.11`) and any relevant details about the fail configuration: Applied profile, building machine...

* :bulb: Request a **new library** to be added:
    - Use the `[request]` label to search the library in the issue tracker in case it was already requested.
    - If not, use the same `[request]` tag in the title of the issue to help identifying them.
    - Indicate the name and the version of the library you would like to have in the repository. Also links to the project's website,
      source download/repository and in general any relevant information that helps creating a recipe for it.

*  :robot: Report **a failure** in the CI system:
    - If you open a Pull Request and get an unexpected error you might comment in the failing PR.
    - If the service or repository is down or failing, use the `[service]` tag in the title of a new issue to help identifying them.

If your issue is not appropriate for a public discussion, please contact us via e-mail at `info@conan.io`. Thanks!


### License

All the Conan recipes in this repository are distributed under the [MIT](LICENSE) license. There
are other files, like patches or examples used to test the packages, that could use different licenses,
for those files specific license and credit must be checked in the file itself.
