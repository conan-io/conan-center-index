# Labels

We use [GitHub labels](https://github.com/conan-io/conan-center-index/labels) to signal the status
of pull-requests and issues. Here you can find more information about the ones that have some
special meaning:

<!-- toc -->
## Contents

  * [Bump dependencies](#bump-dependencies)
  * [Bump version](#bump-version)
  * [Infrastructure](#infrastructure)
  * [Stale](#stale)
  * [Unexpected Error](#unexpected-error)
  * [User-approval pending](#user-approval-pending)
  * [Library Request](#library-request)
  * [Question](#question)
  * [Upstream Update](#upstream-update)
  * [conan.io/center](#conaniocenter)<!-- endToc -->

## Bump dependencies

Label [`Bump dependencies`](https://github.com/conan-io/conan-center-index/pulls?q=is%3Aopen+is%3Apr+label%3A%22Bump+dependencies%22+)
is assigned by the bot to pull-requests that are just upgrading the version of the requirements that were already in the
recipe.

> These pull-requests will be merged right away without requiring any approval (CI and CLA checks must have passed).

If the pull request modifies anything else, the label won't be assigned, we need to be very careful about false positives.

## Bump version

Label [`Bump version`](https://github.com/conan-io/conan-center-index/pulls?q=is%3Aopen+is%3Apr+label%3A%22Bump+version%22)
is assigned by the bot to pull-requests that are just adding a new version of the library. The new version should satisfy
some extra conditions: sources should provide from the same URL domain as previous versions and the version itself should
be valid semver.

> These pull-requests will be merged right away without requiring any approval (CI and CLA checks must have passed).

If the pull request modifies anything else, the label won't be assigned, we need to be very careful about false positives.

## Infrastructure

Label [`infrastructure`](https://github.com/conan-io/conan-center-index/pulls?q=is%3Aopen+is%3Apr+label%3Ainfrastructure) is
manually assigned to pull requests that are waiting for something on the infrastructure side. Usually they are blocked and
cannot succeed because they need some tools, more memory,... these pull requests won't be marked as `stale`.

## Stale

Label [`stale`](https://github.com/conan-io/conan-center-index/pulls?q=is%3Aopen+is%3Apr+label%3Astale) is assigned to
pull requests without any activity during a long period of time. These pull requests will be closed if they don't get
any further activity.

## Unexpected Error

Label [`Unexpected Error`](https://github.com/conan-io/conan-center-index/pulls?q=is%3Aopen+is%3Apr+label%3A%22Unexpected+Error%22)
is assigned by the CI when the process finishes abnormally.
Usually it is some _random_ internal error and it won't happen next time the CI runs.
The CI will re-start your build automatically, the Github check `continuous-integration/jenkins/pr-merge`
will be changed to the status `Pending — This commit is being built` to signalize as running.

> **Note**: Manually restarting a new build, by closing/opening the PR, will be added to the end of the CI build queue.

## User-approval pending

Label [`User-approval pending`](https://github.com/conan-io/conan-center-index/pulls?q=is%3Aopen+is%3Apr+label%3A%22User-approval+pending%22)
signals the pull request that have been submitted by an user who is not yet approved in ConanCenter. Once the user is
approved these pull requests will be triggered again automatically.

## Library Request

Request a new package to be created.

## Question

Further information is requested. Usually these are for issue where help is needed to solve a specific issue. These are a great way
to look for advice or recommendation about making changes to recipes.

## Upstream Update

Request a bump of a new package version.

## conan.io/center

Issues and features related to Web UI.
