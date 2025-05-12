# Review process

Behind the scenes of conan-center-index, there is a heavily automated process to test and merge pull requests.
As there is a lot of activity from many users and many PRs are opened every day.
conan-center-index tries to make the process as smooth and simple as possible for the contributors, providing feedback in PRs. In this document will explain the review process in detail.

<!-- toc -->
## Contents

  * [Green build](#green-build)
    * [Unexpected error](#unexpected-error)
  * [Avoiding conflicts](#avoiding-conflicts)
  * [Getting your pull request reviewed](#getting-your-pull-request-reviewed)
    * [Rule of 2 reviews](#rule-of-2-reviews)
    * [Reviews from others](#reviews-from-others)
    * [Addressing review comments](#addressing-review-comments)
  * [Package available to consume](#package-available-to-consume)
  * [Updating web front end](#updating-web-front-end)
  * [Stale PRs](#stale-prs)<!-- endToc -->

## Green build

The first important prerequisite is ensuring your PR is green (build is successful).
It requires a bit of patience, because there are many PRs running and we're building a lot of configurations for a numerous versions of libraries.
Keep attention to the error messages from the check tab on your PR, and address all the build failures.
The checks tries to provide all the helpful information needed to understand and reproduce an issue.

If you struggle to fix build errors yourself, you may want to ask for help from other users by mentioning (`@conan-io/barbarians`) group in the pull request comments.

### Unexpected error

Sometimes, build fails with an unexpected error (e.g Pre-Checks hangs forever). This indicates an infrastructure problem, and usually it's unrelated to the changes within PR itself. When this occurs, please, ping `@conan-io/barbarians` in your PR describing your situation.

## Avoiding conflicts

Right now, the check `Related Pull Requests` shows other PRs that are affecting the recipe and may result in conflicts, so it's the contributor's responsibility to periodically check for the conflicts. Pull Requests that have merge conflicts can't be merged, and all the conflicts have to be resolved first.

In case a PR that affects your recipe is merged first, then, you have to [synchronize your branch](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork) to take into account the latest changes in the main branch. This is important for ConanCenter to ensure it is building the correct recipe revision.

One trick is to look the [List of open pull requests broken down by recipe](https://github.com/conan-io/conan-center-index/discussions/24240) which can anticipate possible problems.

## Getting your pull request reviewed

Each PR must be reviewed before it will be merged. Extra reviews are welcome and appreciated, but the Conan team reviews are required.

### Rule of 2 reviews

At least 2 approving reviews are required from maintainers are mandatory to merge a PR.

Approvals are only counted if they are associated with the latest commit in the PR, while "Change requested" ones (from the Conan team) will persist even if there are new commits.

### Reviews from community

All reviews are still valuable and very helpful.

### Addressing review comments

Please ensure to address the review comments and respond to them in order to get your PR approved and finally merged.
Be polite and open to suggestions. Also, please, read the [code of conduct](code_of_conduct.md) to understand the expected behavior in the community.

## Package available to consume

New packages are promoted from the internal repository to ConanCenter.
The process can take few minutes, so please, consider a *grace period* and understand that the package won't be available immediately.

## Updating web front end

[ConanCenter](https://conan.io/center/) doesn't directly pull the information from conan-center-index
repository.  Instead, it's updated by the conan center CI job as its own step. The metadata from the conan repository is
converted to the format the web-front-end understands and then sent to it as a scheduled update. As a result, there may occasionally be delays in updating the web-front-end.
That may explain the fact there are moments when the information showed in the frontend doesn't match the actual state on the ConanCenter repository.

## Stale PRs

Conan Center Index uses [stale bot](https://github.com/probot/stale) to close abandoned pull requests. It's configured by [stale.yml](../.github/workflows/stale.yml). When a pull request gets stale, we encourage anyone to take ownership of the PR (even submit changes to the author's branch if possible) so existing work doesn't get lost when the pull request is closed without merging.
