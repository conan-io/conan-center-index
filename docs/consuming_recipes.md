# Consuming recipes

ConanCenter has always maintained recipes consumers need to have an up to date client for the best experience.
The reason is there are constantly improvements and fixes being made, sometimes those require new Conan features
to be possible. There are usually waves of new features, patches and fixes that allow for even better quality recipes.

<!-- toc -->
## Contents

  * [Breaking changes](#breaking-changes)
  * [Expected Environment](#expected-environment)
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

- **New Conan Version**: Conan keeps evolving and adding new features, and ConanCenter is committed in this
   as well, and tries to prepare the user base to these new features in order to ease the migration to new versions.

   New recipe revisions can take into account changes that are introduced in new Conan client
   version, sometimes these changes modify some experimental behavior without modifying recipe syntax.

This use case is covered by the [`required_conan_version`](https://docs.conan.io/2/reference/conanfile/attributes.html#required-conan-version) feature.
It will substitute the syntax error by one nicer error provided by Conan client.

To be sure that people using these new experimental features are using the required Conan version and testing the actual behavior
of those features (feedback about them is very important to Conan).

## Expected Environment

If you are installing packages and we host binary packages for your requested configuration, in most cases you will only need the [Conan client](https://docs.conan.io/2/installation.html) installed on your system.

However, if the packages need to be built from source, for instance, when using `--build=missing` or `conan create`, additional tools and dependencies are required. These vary depending on the package but typically include a compiler toolchain, CMake, and other build utilities.

Conan Center Index recipes assume the following components are already installed in your system:

<table><thead>
  <tr>
    <th>Requirement</th>
    <th>Linux</th>
    <th>Windows</th>
    <th>macOS</th>
  </tr></thead>
<tbody>
  <tr>
    <td>Conan 2.x client</td>
    <td colspan="3">See <a href="https://docs.conan.io/2/installation.html">installation instructions</a></td>
  </tr>
  <tr>
    <td>CMake 3.15 or higher</td>
    <td colspan="3">Linux: check your system package manager (recommended)<br>All platforms: consider installing directly from (<a href="https://cmake.org/download/">CMake downloads</a>)<br><br>Alternatively: you can add it as a `tool_requires` in your profile (Conan <a href="https://docs.conan.io/2/reference/config_files/profiles.html#tool-requires">docs</a>)</td>
  </tr>
  <tr>
    <td>Compiler toolchain</td>
    <td>Complete compiler suite with helper executables (e.g. `strip`, `ar`)<br><br>Install via `build-essential` (Debian-based distros) or equivalent</td>
    <td>Visual Studio with C++ development components<br>Required: MSVC, Windows SDK, C++ CMake TOols</td>
    <td>Xcode or Command Line Tools<br>Install via macOS App Store<br>or run the `xcode-select --install` command</td>
  </tr>
  <tr>
    <td>Build tools</td>
    <td>GNU Make, Perl (typically covered by `build-essential`)<br><br>Python (only required by some recipes)</td>
    <td>Python (only required by some recipes)<br><a href="https://www.python.org/downloads/windows/">installation instructions</a><br><br>Alternatively, it's possible to install it via the Visual Studio installer</td>
    <td>GNU make, Perl, Python<br>Usually these do not require a separate installation if Xcode/CLT are installed. </td>
  </tr>
  <tr>
    <td>pkg-config</td>
    <td>Please install via system package manager<br>and define `tools.gnu:pkg_config` in the `[conf]` section of your profile</span></td>
    <td>(not required)</td>
    <td>(not required)</td>
  </tr>
</tbody></table>

> **Note**: Using a dedicated Python virtual environment for Conan is highly recommended to avoid conflicts with other Python packages.


## Isolate your project from upstream changes

This has always been a concern from ConanCenter consumers.

Conan is very flexible; you can add your own remote or modify your client’s configuration for more granularity. We see the majority of Conan users hosting their own remote, and only consuming packages from there. For production this is the recommended way to add some infrastructure to ensure stability. This is generally a good practice when relying on package managers - not just Conan.

Here are a few choices:

- [Cache recipes in your own ArtifactoryCE](https://docs.conan.io/2/devops/devops_local_recipes_index.html) - recommended for production environments

Using your own ArtifactoryCE instance is easy. You can [deploy it on-premise](https://conan.io/downloads.html) or use a
[cloud provided solution](https://jfrog.com/start-free) for **trial**.
Your project should [use only this remote](https://docs.conan.io/2/reference/commands/remote.html#conan-remote-add) and new recipe
revisions are only pushed to your Artifactory after they have been validated in your project.

The minimum solution, if still choosing to rely on ConanCenter directly, involves small changes to your client configuration by pinning the revision of every reference you consume in your project using the following:

- [recipe revision (RREV)](https://docs.conan.io/2/tutorial/versioning/revisions.html#using-revisions) can be added to each requirement.
  Instead of `fmt/9.1.0` you can add a pound (or hashtag) to the end followed by the revision `fmt/9.1.0#c93359fba9fd21359d8db6f875d8a233`.
- [Lockfiles](https://docs.conan.io/2/tutorial/versioning/lockfiles.html) can be created with the `conan lock create` and read with by
  adding `--lockfile=conan.lock` to `conan install` or `conan create` commands. See the [lockfile introduction](https://docs.conan.io/2/tutorial/consuming_packages/intro_to_versioning.html#lockfiles) for more information.

Both of these give you better control and will allow you to choose when to upgrade your Conan client.

---

This repository will keep evolving, and Conan will release new features. Even if these breaking
changes can cause some disruption, we think that they are needed and they contribute
to improve the overall experience in the C++ ecosystem.
