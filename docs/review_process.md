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
    * [Rule of 3 reviews](#rule-of-3-reviews)
    * [Reviews from others](#reviews-from-others)
    * [Addressing review comments](#addressing-review-comments)
  * [Automatic Merges](#automatic-merges)
    * [Merge](#merge)
    * [Upload](#upload)
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
It requires a bit of patience, because there are many PRs are running, and we're building a lot of configurations for a numerous versions of libraries.
Keep attention to the error messages from the bot, and address all the build failures.
The bot tries to provide all the helpful information needed to understand and reproduce an issue, such as:

- The profile that failed (in other words, the configuration: architecture, operation system, compiler, etc.)
- Failed command line (it might have failed on early stages, like recipe syntax errors, hook errors or later stages, like build or test).
- Logs containing the actual output of the build process (note that some logs like *configure.log* or *CMakeError.log* are not captured, only stdout/stderr).

If you struggle to fix build errors yourself, you may want to ask for help from other users by mentioning (`@<user>`) individual users in the pull request comments.

### Unexpected error

Sometimes, build fails with `Unexpected error` message. This indicates an infrastructure problem, and usually it's unrelated to the changes within PR itself.
Keep in mind conan-center-index is still _under development_, and there can be some instabilities. Especially, as we're using lots of external services,
which might be inaccessible (GitHub API, docker hub, etc.) and may result in intermittent failures.
So, what to do once `Unexpected error` was encountered? You may consider re-running the build by closing your pull request, waiting 15 seconds, and then re-opening it again.

Sometimes it's necessary to restart the build several times.
If an `Unexpected error` persists, tag [@jgsogo](https://github.com/jgsogo) and [@danimtb](https://github.com/danimtb) asking for the help with CI.
Alternatively, just [open a new issue](https://github.com/conan-io/conan-center-index/issues/new/choose).

## Avoiding conflicts

It's recommended to rebase your changes on top of the master branch to avoid conflicts.
Right now, neither GitHub itself nor conan-center-bot notify about merge conflicts, so it's the contributor's responsibility to periodically check for the conflicts.
Obviously, PRs that have merge conflicts are never merged, and all the conflicts have to be resolved first.

## Draft

Draft pull requests are also never merged. The same applies for PRs with the `WIP` keyword (stands for `Work in Progress`) in the title - GitHub considers them drafts as well.
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

The list includes conan-center-index contributors who are very active and proven to be trusted - they frequently submitted pull requests and provide their own useful reviews:

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

The list is not constant and will change periodically based on contribution.
That also means you can be included in this list as well - submit PRs and provide reviews, and in time you may be added as a trusted contributor.

### Rule of 3 reviews

At least 3 reviews are required for an approval, and at least one of them has to be from the official reviewers.
So, it might be 1 official + 2 community, or 3 official, but it couldn't be just 3 community reviews.
Approvals are only counted if they are associated with the latest commit in the PR, while "Change requested" ones (from the Conan team) will persist even if there are new commits. Don't hesitate to dismiss old reviews if the issues have already been addressed.

### Reviews from others

All reviews are still valuable and very helpful. Even if you're not listed as an official or community reviewer counted by the bot, your reviews are still welcome, so please do not hesitate to provide them.

### Addressing review comments

Please ensure to address the review comments and respond to them in order to get your PR approved and finally merged.
It doesn't always mean accepting all the suggestions, but at least providing a response, so people can understand your position.

## Automatic Merges

The bot runs Automatic Merges every 30 minutes. Currently, it can only merge a single PR in this timeframe, so there is a theoretical limit of 48 PRs merged per day (in practice, it's even less for reasons listed below).
PR is selected for the merge only if:

- Author is already [approved](https://github.com/conan-io/conan-center-index/issues/4).
- Author has signed CLA.
- PR is not a Draft or WIP.
- PR has a green status (successful build).
- PR doesn't have merge conflicts with `master` branch.
- PR has 3 approved reviews (as described above).
- PR does not have any [official reviewers](#official-reviewers) requesting changes
- Master build is not running already (see below)

If these conditions are fulfilled, the PR is merged (associated issues are automatically closed), and then the build of master is launched.

### Merge

After merging a pull request, if an actual merge happened (for instance, the recipe changed in PR was already updated in master by the time PR merged),
it will introduce a new recipe revision. Therefore, the build should be run one more time, so the master build is launched.
In reality this could happen frequently enough if there are multiple PRs aiming to update the same recipe (even if they touch different files in the same recipe).
Such builds can take hours for big packages (like boost), blocking other merges for a while.
So we really appreciate it if changes in master to the same recipe are already merged into the proposed PR.

### Upload

Even if there is no new revision introduced, CI still needs to publish artifacts from the internal repository to ConanCenter, and it may also take hours for big enough packages.
This also blocks further merges until upload is finished. It also explains why new packages are not immediately available for consumption after the merge, and there is a grace period to wait for their availability.

### Updating web front end

[ConanCenter](https://conan.io/center/) doesn't directly pull the information from conan-center-index
repository.  Instead, it's updated by the conan center CI job as its own step. The metadata from the conan repository is
converted to the format the web-front-end understands and then sent to it as a scheduled update. As a result, there may occasionally be delays in updating the web-front-end.
That may explain the fact there are moments when the information showed in the frontend doesn't match the actual state on the ConanCenter repository.

## Stale PRs

Conan Center Index uses [stale bot](https://github.com/probot/stale) to close abandoned pull requests. It's configured by [stale.yml](.github/stale.yml). When a pull request gets stale, we encourage anyone to take ownership of the PR (even submit changes to the author's branch if possible) so existing work doesn't get lost when the pull request is closed without merging.
