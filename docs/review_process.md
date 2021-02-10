# Review process

Behind the scenes of conan center index, there is a pretty complicated and heavily automated process to review and merge pull requests.
As there is a lot of activity from many users and various bots (e.g. bumping versions or updating conventions), many PRs are opened every day.
CCI tries to make process as smooth and simple as possible for the contributors, 
but it requires complicated logic under the hood, and sometimes the logic might not look that obvious for the newcomers, 
so this document intends to describe the internal process in detail.

## [conan-center-bot](https://github.com/conan-center-bot)

In general, reviews are driven by the automated [bot](https://github.com/conan-center-bot). The bot is responsible for:

- adding or removing labels (such as [No Beta User](https://github.com/conan-io/conan-center-index/pulls?q=is%3Apr+is%3Aopen+label%3A%22No+Beta+user%22) or [Docs](https://github.com/conan-io/conan-center-index/pulls?q=is%3Apr+is%3Aopen+label%3ADocs))
- writing comments (most of the time, it's a build status, either failure with logs or success)
- merging pull requests
- closing issues (side effect of merging pull requests)
- starting CI builds
- assigning CI status (running/failed/successful)

## green build

The first important prerequisite is ensuring your PR is green (build is successful).
It requires a bit of patience, because there are many PRs are running, and we're building a lot of configurations for a numerous versions of libraries.
Keep attention to the error messages from the bot, and address all the build failures.
The bot tries to provide all the helpful information needed to understand and reproduce an issue, such as:

- the profile that failed (in other words, the configuration - architecture, operation system, compiler, etc.)
- failed command line (it might have failed on early stages - e.g. recipe syntax errors, or later stages, like build or test)
- logs (contains actual output of the build process - not that some important logs like `configure.log` or `CMakeError.log` are not captured, it's just stdout/stderr)

If you struggle to fix build errors yourself, you always may ask for the help, either by tagging individual users, or by adding label [Help Wanted](https://github.com/conan-io/conan-center-index/pulls?q=is%3Aopen+is%3Apr+label%3A%22help+wanted%22).

### Unexpected error

Sometimes, build fails with `Unexpected error` message. This indicates an infrastructure problem, and usually it's unrelated to the changes within PR itself.
Keep in mind CCI is still in early access (consider it beta), and there are still some instabilities. Especially, as we're using lots of external services,
which might be inaccessible (GitHub API, docker hub, etc.) and may result in intermittent failures.
So, what to do once `Unexpected error` was encountered? You may consider re-running the build, and there are several ways to do it:

- do an empty commit: `git commit --allow-empty`
- update the last commit: `git commit --amend --no-edit && git push -f`
- close pull request, wait 15 seconds, re-open pull request

Sometimes it's necessary to restart the build several times.
If an `Unexpected error` persists, you may assign an [Infrastructure](https://github.com/conan-io/conan-center-index/pulls?q=is%3Apr+is%3Aopen+label%3ADocs+label%3Ainfrastructure) label and tag [@jgsogo](https://github.com/jgsogo) and [@danimtb](https://github.com/danimtb) asking for the help with CI.
Alternatively, just [open a new issue](https://github.com/conan-io/conan-center-index/issues/new/choose).

## avoiding conflicts

It's recommended to rebase your changes on top of the master branch to avoid conflicts.
Right now, neither GitHub itself nor conan-center-bot notify about merge conflicts, so it's the contributor's responsibility to periodically check for the conflicts.
Obviously, PRs that have merge conflicts are never merged, and all the conflicts have to be resolved first.

## draft

Draft pull requests are also never merged. The same applies for PRs with the `WIP` keyword (stands for `Work in Progress`) in the title - GitHub considers them drafts as well.
Once you're done with your changes, remember to convert from "Draft" to "Normal" pull request and remove WIP keyword from the title.

## getting PR reviewed

Each PR must be reviewed by several reviewers before it will be merged. It cannot be just reviews from random people, we have two categories of reviewers:

### official reviewers

The list includes only official conan developers (JFrog employees):

- [@memsharded](https://github.com/memsharded)
- [@lasote](https://github.com/lasote)
- [@danimtb](https://github.com/danimtb)
- [@jgsogo](https://github.com/jgsogo)
- [@czoido](https://github.com/czoido)
- [@solvingj](https://github.com/solvingj)
- [@sse4](https://github.com/sse4)
- [@uilianries](https://github.com/uilianries)

### community reviewers

The list includes conan center index contributors who are very active and proven to be trusted - they frequently submitted pull requests and provide their own useful reviews:

- [@madebr](https://github.com/madebr)
- [@SpaceIm](https://github.com/SpaceIm)
- [@ericLemanissier](https://github.com/ericLemanissier)
- [@prince-chrismc](https://github.com/prince-chrismc)
- [@Croydon](https://github.com/Croydon)
- [@intelligide](https://github.com/intelligide)
- [@theirix](https://github.com/theirix)
- [@gocarlos](https://github.com/gocarlos)

The list is not constant and will change periodically based on contribution.
That also means you can be included in this list as well - submit PRs and provide reviews, and in time you may be added as a trusted contributor.

### Rule of 3 reviews

At least 3 reviews are required for an approval, and at least one of them has to be from the official reviewers.
So, it might be 1 official + 2 community, or 3 official, but it couldn't be just 3 community reviews.

### Reviews from others

All reviews are still valuable and very helpful. Even if you're not listed as an official or community reviewer counted by the bot, your reviews are still welcome, so please do not hesitate to provide them.

### Addressing review comments

Please ensure to address the review comments and respond to them in order to get your PR approved and finally merged.
It doesn't always mean accepting all the suggestions, but at least providing a response, so people can understand your position.

## Automatic Merges

The bot runs Automatic Merges every 30 minutes. Currently, it can only merge a single PR in this timeframe, so there is a theoretical limit of 48 PRs merged per day (in practice, it's even less for reasons listed below).
PR is selected for the merge only if:

- author is a [beta user](https://github.com/conan-io/conan-center-index/issues)
- author has signed CLA
- PR is not a Draft or WIP
- PR has a green status (successful build)
- PR doesn't have merge conflicts with `master` branch
- PR has 3 approved reviews (rule described above)
- master build is not running already (see below)

If these conditions are fullfilled, the PR is merged (associated issues are automatically closed), and then build of master is launched

### Merge

If there is an actual merge to happen (for instance, the recipe changed in PR was already updated in master by the time PR merged), 
it will introduce a new recipe revision. Therefore, the build should be run one more time, so the master build is launched.
In reality this could happen frequently enough if there are multiple PRs aiming to update the same recipe (even if they touch different files in the same recipe).
Such builds can takes hours for big packages (like boost), blocking other merges for a while.

### Upload

Even if there is no new revision introduced, CI still needs to publish artifacts from the internal repository to the conan center index, and it also currently may take hours for big enough packages.
This also blocks further merges until upload is finished. It also explains why new packages are not immediately available for consumption after the merge, and there is a grace period to wait for they availability.

### Updating web front end

Conan center [web front-end](https://conan.io/center/) doesn't directly pull the information from the conan center index 
repository.  Instead, it's updated by the conan center CI job as its own step. The metadata from the conan repository is 
converted to the format the web-front-end understands and then sent to it as a scheduled update. As a result, there may occasionally be delays in updating the web-front-end.
That may explain the fact there are moments then information is front end doesn't match the actual state on the conan center repository.
