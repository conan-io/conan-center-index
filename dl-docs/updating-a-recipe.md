# Updating a recipe

<!-- mdformat-toc start --slug=github --no-anchors --maxlevel=6 --minlevel=2 -->

- [Adding a new revision of a recipe](#adding-a-new-revision-of-a-recipe)
  - [In conjunction with a contribution to `conan-io/conan-center-index`](#in-conjunction-with-a-contribution-to-conan-ioconan-center-index)
  - [At DL only](#at-dl-only)
- [Testing the updated recipe with DL projects](#testing-the-updated-recipe-with-dl-projects)
- [Bringing updates to production](#bringing-updates-to-production)

<!-- mdformat-toc end -->

This document will cover updating a recipe, but the same steps apply to making a
new recipe; it just starts from nothing rather than modifying a recipe that's
there.

## Adding a new revision of a recipe

### In conjunction with a contribution to `conan-io/conan-center-index`

You can do this procedure work with packages you are contributing upstream, or
to get changes that others are making before they get fully approved by the
conan-io team.

This general procedure is the same whether making fixes to a recipe, or adding a
new version of a software package. If you're adding a new version of the
software package, see how versions are specified in the
[recipe files structure](https://github.com/conan-io/conan-center-index/tree/master/docs/adding_packages#recipe-files-structure)
at conan-io.

1. First, make the changes in a fork of the
   [conan-io/conan-center-index](https://github.com/conan-io/conan-center-index)
   repository, according to the requirements of the
   [CONTRIBUTING.md](https://github.com/conan-io/conan-center-index/blob/master/CONTRIBUTING.md)
   document there. You'll need to use a fork on github.com for this.
2. Create a pull request at `conan-io/conan-center-index`.
3. Create a branch from `upstream/develop` (where `upstream` is the
   `datalogics/conan-center-index` repository on Octocat).
4. Get the HTTPS URL of the fork with the changes. From the PR on github.com,
   you can click on the "from" branch in the PR header to get to the repository.
   Then click on **Code**, choose **HTTPS**, and click the button to the right
   of the URL to copy the URL.
5. Do a `git pull --no-ff <HTTPS URL of the fork> <branch-with-changes>`. A
   remote is really shorthand for a URL of a remote repository. It's not
   necessary to create a remote to pull a branch from a remote repository.
6. Push the changes up to your `conan-center-index` fork on _Octocat_.
7. Open a PR on Octocat against `develop`.

An example of this procedure can be found in the pull request
[datalogics/conan-center-index#32](https://octocat.dlogics.com/datalogics/conan-center-index/pull/32).
That pull request had changes to libdeflate that we needed to bring in early.

The `git pull` command in the case of datalogics/conan-center-index#32 was

```bash
git pull --no-ff https://github.com/SpaceIm/conan-center-index.git fix/libdeflate-install
```

### At DL only

1. Check out your fork of `conan-center-index` on Octocat.
2. Create a branch based on `upstream/develop`
3. Make changes to a recipe as needed.
4. Push the changes up to Octocat.
5. Open a PR on Octocat against `develop`.

## Testing the updated recipe with DL projects

Before bringing the updates into production, test with existing DL projects. To
do this, create a draft PR in one or more projects, and alter the Jenkins file
to set the environment variable `DL_CONAN_CENTER_INDEX=staging`. Also see the
[documentation](using-the-ccci-repositories.md#building-against-the-staging-repository)
on using the staging repository.

## Bringing updates to production

To make an update available to production,
[run the appropriate Jenkins job to merge staging to production](jenkins-jobs.md#merging-develop-to-master-to-put-recipes-into-production).
