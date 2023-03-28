# How to bump a package version for an existing recipe in ConanCenterIndex?

Once a recipe is approved and merged to ConanCenterIndex, it may need to be updated with new versions released by the upstream.
When someone needs a new package version that is not available in ConanCenterIndex, that person can open an issue [resquesting a new version](https://github.com/conan-io/conan-center-index/issues/new?assignees=&labels=upstream+update&template=package_upstream_update.yml&title=%5Brequest%5D+%3CLIBRARY-NAME%3E%2F%3CLIBRARY-VERSION%3E).
Or, by opening a pull request changing and adding that needed version, this is called a `bump version`.
The [build service](adding_packages/README.md#the-build-service) bumping process is limited to pull requests which **only** adds a new package version and nothing more. Removing older versions, or updating
the recipe will disqualify a pull request from the `Bump version` [review process](review_process.md)

## Choosing which version should be updated

The first step is checking the version which should be added from the upstream. Please, avoid adding multiple versions which you do not
need. Adding a new version will increase the building time and storage for each new package configuration.

Once you detect which version should be updated, please, first check if the project `license` keeps the same.

> In case you need to update attributes, dependencies versions, patches, or anything besides the package version in `conandata.yml` and `config.yml`,
  then your pull request will not be classified as bump version.

## What should be modified when bumping a version?

Only the `config.yml` and `conandata.yml` should be updated with that new version:

```yaml
# config.yml
versions:
  "1.1.0":       <-- New version added. It should be protected by quotes
    folder: all  <-- Folder name where conandata.yml is installed
  "1.0.0":
    folder: all
```

```yaml
# all/conandata.yml
sources:
  "1.1.0":       <-- New version added
    url: "https://example.com/repo/exameple-1.1.0.tar.gz"
    sha256: "b3a24de97a8fdbc835b9833169501030b8977031bcb54b3b3ac13740f846ab30"
  "1.0.0":
    url: "https://example.com/repo/exameple-1.0.0.tar.gz"
    sha256: "91844808532e5ce316b3c010929493c0244f3d37593afd6de04f71821d5136d9"
```

In case a patch should be re-used, it should be present in `conandata.yml` to the specific version as well.

## Reviewing and merging

Bumping version PRs follow the same regular [review process](review_process.md), except for being merged automatically
as listed on [Labels](labels.md#bump-version) section.
