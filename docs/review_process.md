# Review process

Behind the scenes of conan-center-index, there is a heavily automated process to test and merge pull requests.
As there is a lot of activity from many users and various bots (e.g. bumping versions or updating conventions), many PRs are opened every day.
conan-center-index tries to make the process as smooth and simple as possible for the contributors, providing feedback in PRs. In this document will explain the review process in detail.

<!-- toc -->
## Contents

  * [conan-center-bot](#conan-center-bot)
  * [Green build](#green-build)
    * [Unexpected error](#unexpected-error)
  * [Avoiding conflicts](#avoiding-conflicts)
  * [Draft](#draft)
  * [Getting your pull request reviewed](#getting-your-pull-request-reviewed)
    * [Official reviewers](#official-reviewers)
    * [Community reviewers](#community-reviewers)
    * [Rule of 2 reviews](#rule-of-2-reviews)
    * [Reviews from others](#reviews-from-others)
    * [Addressing review comments](#addressing-review-comments)
  * [Automatic Merges](#automatic-merges)
    * [Merge](#merge)
    * [Package available to consume](#package-available-to-consume)
    * [Updating web front end](#updating-web-front-end)
  * [Stale PRs](#stale-prs)<!-- endToc -->

## [conan-center-bot](https://github.com/conan-center-bot)

In general, reviews are driven by the automated [bot](https://github.com/conan-center-bot). The bot is responsible for:

- Adding or removing labels (such as [Bump version](https://github.com/conan-io/conan-center-index/pulls?q=is%3Apr+is%3Aopen+label%3A%22Bump+version%22) or [Docs](https://github.com/conan-io/conan-center-index/pulls?q=is%3Apr+is%3Aopen+label%3ADocs)).
- Writing comments (most of the time, it's a build status, either failure with logs or success).
- Merging pull requests.
- Closing issues (after merging pull requests with GitHub keywords).
- Starting CI builds.
- Assigning CI status (running/failed/successful).

## Green build

The first important prerequisite is ensuring your PR is green (build is successful).
It requires a bit of patience, because there are many PRs running and we're building a lot of configurations for a numerous versions of libraries.
Keep attention to the error messages from the bot, and address all the build failures.
The bot tries to provide all the helpful information needed to understand and reproduce an issue, such as:

- The profile that failed (in other words, the configuration: architecture, operation system, compiler, etc.)
- Failed command line (it might have failed on early stages, like recipe syntax errors, hook errors or later stages, like build or test).
- Logs containing the actual output of the build process (note that some logs like *configure.log* or *CMakeError.log* are not captured, only stdout/stderr).

If you struggle to fix build errors yourself, you may want to ask for help from other users by mentioning (`@<user>`) individual users in the pull request comments.

### Unexpected error

Sometimes, build fails with `Unexpected error` message. This indicates an infrastructure problem, and usually it's unrelated to the changes within PR itself.

To learn more, checkout the [label definition](labels.md#unexpected-error).

## Avoiding conflicts

Right now, neither GitHub itself nor conan-center-bot notify about merge conflicts, so it's the contributor's responsibility to periodically check for the conflicts. Pull Requests that have merge conflicts can't be merged, and all the conflicts have to be resolved first.

Please [synchronize your branch](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork) to take into account the latest changes in the main branch. This is important for ConanCenter to ensure it is building the correct recipe revision, see [this comment](https://github.com/conan-io/conan-center-index/pull/8797#discussion_r781993233) for details. One trick is to look out for comments from the [Community's Conflict PR Bot](https://github.com/prince-chrismc/conan-center-index/blob/patch-41/docs/community_resources.md#bots) which can anticipate possible problems.

## Draft

Draft pull requests are also never merged, and they won't likely be reviewed.
Once you're done with your changes, remember to convert from "Draft" to "Normal" pull request.

## Getting your pull request reviewed

Each PR must be reviewed by several reviewers before it will be merged. It cannot be just reviews from random people, we have two categories of reviewers:

### Official reviewers

The list includes only official Conan developers:

- [@memsharded](https://github.com/memsharded)
- [@lasote](https://github.com/lasote)
- [@danimtb](https://github.com/danimtb)
- [@jgsogo](https://github.com/jgsogo)
- [@czoido](https://github.com/czoido)
- [@sse4](https://github.com/sse4)
- [@uilianries](https://github.com/uilianries)

### Community reviewers

The list includes conan-center-index contributors who are very active and proven to be trusted - they frequently submit pull requests and provide their own useful reviews:

- [@madebr](https://github.com/madebr)
- [@SpaceIm](https://github.com/SpaceIm)
- [@ericLemanissier](https://github.com/ericLemanissier)
- [@prince-chrismc](https://github.com/prince-chrismc)
- [@Croydon](https://github.com/Croydon)
- [@intelligide](https://github.com/intelligide)
- [@theirix](https://github.com/theirix)
- [@gocarlos](https://github.com/gocarlos)
- [@mathbunnyru](https://github.com/mathbunnyru)
- [@ericriff](https://github.com/ericriff)
- [@toge](https://github.com/toge)
- [@AndreyMlashkin](https://github.com/AndreyMlashkin)
- [@MartinDelille](https://github.com/MartinDelille)
- [@dmn-star](https://github.com/dmn-star)

The list, located [here](../.c3i/reviewers.yml),
is not constant and will change periodically based on contribution.
That also means **you can be included in this list** as well - submit PRs and provide reviews, and in time you may be added as a trusted contributor.

### Rule of 2 reviews

At least 2 approving reviews are required, and at least one of them has to be from the official reviewers.
So, it might be 1 official + 1 community, or 2 official, but it couldn't be just 2 community reviews.
Approvals are only counted if they are associated with the latest commit in the PR, while "Change requested" ones (from the Conan team) will persist even if there are new commits. Don't hesitate to dismiss old reviews if the issues have already been addressed.

> **Note** Pull requests labelled as [`Bump version`](https://github.com/conan-io/conan-center-index/pulls?q=is%3Aopen+is%3Apr+label%3A%22Bump+version%22)
> or [`Bump dependencies`](https://github.com/conan-io/conan-center-index/pulls?q=is%3Aopen+is%3Apr+label%3A%22Bump+dependencies%22+) are merged by
> the bot without requiring any approval.

### Reviews from others

All reviews are still valuable and very helpful. Even if you're not listed as an official or community reviewer, **your reviews are very welcome**, so please do not hesitate to provide them.

### Addressing review comments

Please ensure to address the review comments and respond to them in order to get your PR approved and finally merged.
It doesn't always mean accepting all the suggestions, but at least providing a response, so people can understand your position.

## Automatic Merges

The bot runs Automatic Merges every 20 minutes. Currently, it can only merge a single PR in this timeframe, so there is a theoretical limit of ~70 PRs merged per day (in practice, it's even less for reasons listed below).
PR is selected for the merge only if:

- Author is already [approved](https://github.com/conan-io/conan-center-index/issues/4).
- Author has signed CLA.
- PR is not a Draft.
- PR has a green status (successful build).
- PR doesn't have merge conflicts with `master` branch.
- PR has approved reviews (as described above).
- PR does not have any [official reviewers](#official-reviewers) requesting changes
- Master build is not running already (see below)

If these conditions are fulfilled, the PR is merged (associated issues are automatically closed), and then the build of `master` is launched.

The conan-center-bot will perform a [squash and merge](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges#squash-and-merge-your-pull-request-commits). You don't need to rebase
your pull request, we ask you not to do it because it will dismiss any reviews and the reviewer will need to restart.

### Merge

After merging a pull request, if an actual merge happened (for instance, the recipe changed in PR was already updated in `master` by the time PR merged),
it will introduce a new recipe revision. Therefore, the build should be run one more time, so the `master` build is launched.
In reality this could happen frequently enough if there are multiple PRs aiming to update the same recipe (even if they touch different files in the same recipe).
Such builds can take hours for big packages (like boost), blocking other merges for a while.
So we really appreciate it if changes in `master` to the same recipe are already merged into the proposed PR.

### Package available to consume

New packages are promoted from the internal repository to ConanCenter. This process is an internal Artifactory promotion that is quite
fast, nevertheless there are some caches and CDNs that need to be invalidated and propagated before the package is finally available for consumption.
The process can take several minutes, so please, consider a *grace period* and understand that the package won't be available immediately.

### Updating web front end

[ConanCenter](https://conan.io/center/) doesn't directly pull the information from conan-center-index
repository.  Instead, it's updated by the conan center CI job as its own step. The metadata from the conan repository is
converted to the format the web-front-end understands and then sent to it as a scheduled update. As a result, there may occasionally be delays in updating the web-front-end.
That may explain the fact there are moments when the information showed in the frontend doesn't match the actual state on the ConanCenter repository.

## Stale PRs

Conan Center Index uses [stale bot](https://github.com/probot/stale) to close abandoned pull requests. It's configured by [stale.yml](../.github/stale.yml). When a pull request gets stale, we encourage anyone to take ownership of the PR (even submit changes to the author's branch if possible) so existing work doesn't get lost when the pull request is closed without merging.
