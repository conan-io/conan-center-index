# Consuming recipes

ConanCenter has always maintained recipes consumers need to have an up to date client for the best experience.
The reason is there are constantly improvements and fixes being made, sometimes those require new Conan features
to be possible. There are usually waves of new features, patches and fixes that allow for even better quality recipes.

<!-- toc -->
## Contents

  * [Breaking changes](#breaking-changes)
  * [Isolate your project from upstream changes](#isolate-your-project-from-upstream-changes)<!-- endToc -->

## Breaking changes

There can be several causes if a recipe (a new revision) might stopped to work in your project:

- **Fixes in recipes** that modify the libraries they are creating: exported symbols,
   compiler flags, generated files for your build system, CMake target names,...

   Every contributor tries to do their best and reviewers do an amazing work checking that the
   changes are really improving recipes.
- **New Conan features (breaking syntax)** sometimes requires new attributes or statements in recipes.
    If your Conan client is not new enough,
   Conan will fail to parse the recipe and will raise a cryptic Python syntax error.

- **New Conan Version**: Conan keeps evolving and adding new features, especially on its road to Conan 2.0,
   and ConanCenter is committed in this [roadmap](v2_roadmap) as well, and tries to prepare the user base to these
   new features in order to ease the migration to new versions.

   New recipe revisions can take into account changes that are introduced in new Conan client
   version, sometimes these changes modify some experimental behavior without modifying recipe syntax.

This use case is covered by the [`required_conan_version`](https://docs.conan.io/en/latest/reference/conanfile/other.html?highlight=required_conan_version#requiring-a-conan-version-for-the-recipe) feature. It will
substitute the syntax error by one nicer error provided by Conan client.
   
To be sure that people using these new experimental features are using the required Conan version and testing the actual behavior
of those features (feedback about them is very important to Conan).

## Isolate your project from upstream changes

This has always been a concern from ConanCenter consumers.

Conan is very flexible; you can add your own remote or modify your client’s configuration for more granularity. We see the majority of Conan users hosting their own remote, and only consuming packages from there. For production this is the recommended way to add some infrastructure to ensure stability. This is generally a good practice when relying on package managers - not just Conan.

Here are a few choices:

- [Running your own Conan Server](https://docs.conan.io/en/latest/uploading_packages/running_your_server.html) - great for local ad-hoc setups
- [Cache recipes in your own ArtifactoryCE](https://docs.conan.io/en/latest/uploading_packages/using_artifactory.html) - recommended for production environments

Using your own ArtifactoryCE instance is easy. You can [deploy it on-premise](https://conan.io/downloads.html) or use a 
[cloud provided solution](https://jfrog.com/community/start-free) for **free**. Your project should 
[use only this remote](https://docs.conan.io/en/latest/reference/commands/misc/remote.html?highlight=add%20new) and new recipe
revisions are only pushed to your Artifactory after they have been validated in your project.

The minimum solution, if still choosing to rely on ConanCenter directly, involves small changes to your client configuration by pinning the revision of every reference you consume in your project using using:

- [recipe revision (RREV)](https://docs.conan.io/en/latest/versioning/revisions.html) can be added to each requirement.
  Instead of `fmt/9.1.0` you can add a pound (or hashtag) to the end followed by the revision `fmt/9.1.0#c93359fba9fd21359d8db6f875d8a233`.
  This feature needs to be enabled in Conan 1.x, see the [Activation Instructions](https://docs.conan.io/en/latest/versioning/revisions.html#how-to-activate-the-revisions) for details.
- [Lockfiles](https://docs.conan.io/en/latest/versioning/lockfiles.html) can be created with the `conan lock create` and read with by
  adding `--lockfile=conan.lock` to `conan install` or `conan create` commands. See the [lockfile introduction](https://docs.conan.io/en/latest/versioning/lockfiles/introduction.html#) for more information.
  
> **Warning** Please, be aware there are some known bugs related to lockfiles that are not being fixed in Conan v1.x - we are really excited for the 2.0 improvements to be widely used.

Both of these give you better control and will allow you to choose when to upgrade your Conan client.

---

This repository will keep evolving, and Conan will release new features. Even if these breaking
changes can cause some disruption, we think that they are needed and they contribute
to improve the overall experience in the C++ ecosystem.
