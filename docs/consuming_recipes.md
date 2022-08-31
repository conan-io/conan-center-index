# Consuming recipes

Recipes in this repository are evolving continuously, contributors are creating pull-requests
fixing issues and adding new features every day. It is expected that from time to time these
new recipe revisions stop to work in your project.

<!-- toc -->
## Contents

  * [Breaking changes](#breaking-changes)
  * [Isolate your project from upstream changes](#isolate-your-project-from-upstream-changes)
    * [Use your own Artifactory instance](#use-your-own-artifactory-instance)
    * [Use recipe revisions and lockfiles](#use-recipe-revisions-and-lockfiles)<!-- endToc -->

## Breaking changes

There can be several root causes if a recipe (a new revision) stopped to work in your project:

 * **Fixes in recipes** that modify the libraries they are creating: exported symbols,
   compiler flags, generated files for your build system, CMake target names,...

   Every contributor tries to do their best and reviewers do an amazing work checking that the
   changes are really improving recipes.

 * **New Conan features (breaking syntax)**: sometimes Conan introduces a new feature that
   requires new attributes or statements in recipes. If your Conan client is not new enough,
   Conan will fail to parse the recipe and will raise a cryptic Python syntax error.

   This use case is covered by the [`required_conan_version`](https://docs.conan.io/en/latest/reference/conanfile/other.html?highlight=required_conan_version#requiring-a-conan-version-for-the-recipe) feature. It will
   substitute the syntax error by one nicer error provided by Conan client.

 * **New Conan features**: Conan keeps evolving and adding new features in its road to Conan v2,
   and ConanCenter is committed in this roadmap as well, and tries to push the user base to these
   new features in order to ease the migration to new versions.

   New recipe revisions can take into account changes that are introduced in new Conan client
   version, sometimes these changes modify some experimental behavior without modifying recipe syntax.

   When these changes are in the critical path to Conan v2 we can introduce the
   `required_conan_version` statement to be sure that people using these new experimental
   features are using the required Conan version and testing the actual behavior of those
   features (feedback about them is very important to Conan).

## Isolate your project from upstream changes

The minimum solution involves small changes to your Conan client configuration by

* **Pin the version of every reference you consume in your project** using either:
  * [recipe revision (RREV)](https://docs.conan.io/en/latest/versioning/revisions.html): `foo/1.0@#RREV` instead of `foo/1.0` in your conanfile. [Activation Instructions](https://docs.conan.io/en/latest/versioning/revisions.html#how-to-activate-the-revisions)
  * [lockfiles](https://docs.conan.io/en/latest/versioning/lockfiles/introduction.html) (please, be aware there are some [knowns bugs](https://github.com/conan-io/conan/issues?q=is%3Aissue+lockfile) related to lockfiles that are not being fixed in Conan v1.x).

For larger projects and teams it is recommended to add some infrastructure to ensure stability by

 * **Cache recipes in your own Artifactory**: your project should use only this remote and
   new recipe revisions are only pushed to your Artifactory after they have been validated
   in your project.

### Use your own Artifactory instance

Using your own Artifactory instance is not as complicated as it sounds. You can [deploy it
on-premise](https://conan.io/downloads.html) or use a [cloud provided solution](https://jfrog.com/start-free/?isConan=true) for free.

Once you have configured your Artifactory instance, you should ensure that your project is
using only that remote (`conan remote list`). Conan makes it easy to use different configurations
per project (check `CONAN_USER_HOME` env variable) or to store the configuration in some external
file or repository so you can shared and install it using one command (`conan config install ...`).

### Use recipe revisions and lockfiles

If you don't want to deploy and maintain your own Artifactory instance, you can isolate from
changes in upstream recipes in ConanCenter using [recipe revisions](https://docs.conan.io/en/latest/versioning/revisions.html)
and [lockfiles](https://docs.conan.io/en/latest/versioning/lockfiles.html) (please, read linked Conan documentation for more detailed
explanation).

Recipe revisions and lockfiles can be used to define exactly the binary you want to use in
your project. **Nothing is removed from ConanCenter**, even if the recipe is modified and new
binaries are generated for the same configurations, existing binaries are still there, you
just need to instruct Conan to use them even if new ones are available.

**Recipe revisions** are the way to tell Conan to use a specific snapshot of the recipe. It
is a hash added to the reference and can be used in Conan at the same place as regular
revisions:

 * In the command line:

   ```sh
   conan install openssl/3.0.1@#1955937e88f13a02aa4fdae98c3f9fb8
   ```

 * In a `conanfile.txt` file:

   ```txt
   [requires]
   openssl/3.0.1@#1955937e88f13a02aa4fdae98c3f9fb8
   ```

 * In a `conanfile.py` file:

   ```py
   def requirements(self):
       self.requires("openssl/3.0.1@#1955937e88f13a02aa4fdae98c3f9fb8")
   ```

If you use explicit recipe revisions in your project you can be sure that Conan will always use
the same recipe revision of those references. You might get new binaries if the same
configuration (same packageID) is built again for the same recipe revision, but that is not
going to be a _compatibility problem_.

This might not be enough for some projects, where you want
to be sure nothing is modified, not just the revisions you are listing explicitly but also any
other transitive dependency, this is what lockfiles are for.

**Lockfiles** are files where all the information about requirements is written: recipe
revisions, package IDs and package revisions. You can create a lockfile with all the
dependencies for your project once you are happy with them, and use that same lockfile
with every Conan command. Conan will always build the same graph (the locked one) and
will always retrieve the same recipes and binaries.

Then, it would be up to you to generate a new lockfile if you want to introduce new revisions
for existing references.

The two basic commands you need to know ([full docs here](https://docs.conan.io/en/latest/versioning/lockfiles.html)):

 * Create lockfile from `conanfile.txt` file:

   ```sh
   conan lock create conanfile.txt --lockfile-out=locks/project.lock
   ```

 * Consume a lockfile:

   ```sh
   conan install conanfile.txt --lockfile=locks/project.lock
   ```

If your project is managing several configurations, you would probably like to have a look to [base lockfiles](https://docs.conan.io/en/latest/versioning/lockfiles/configurations.html#base-lockfiles) and [lockfile bundles](https://docs.conan.io/en/latest/versioning/lockfiles/bundle.html) in the documentation.

---

This repository will keep evolving, and Conan will release new features. Even if these breaking
changes can cause some disruption, we think that they are needed and they contribute
to improve the overall experience in the C++ ecosystem.
