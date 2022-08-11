# Road to Conan v2

<!-- toc -->
## Contents<!-- endToc -->

> ⚠️ **Note.-** This document is not a [guide about how to migrate recipes to Conan v2](v2_migration.md).

> ⚠️ **Note.-** This is a working document that will be updated as we walk
> this path. There are no dates intentionally, and if any they should be
> considered as an estimation, there are still some unknowns to provide
> certain steps and dates.

Conan v2 is under heavy development and it will be released in the
following months. It comes with many improvements that will benefit
recipes and users, and we are willing to adopt it.

It is a new major version that will come with many breaking changes. Lot
of the features and syntax that we were used to in Conan v1 will no longer
be available and will be superseeded by improved alternatives. All these
alternatives should be backported to v1.x releases, so **there will be a
subset of features that will work using Conan v1 and v2**.

**Our main goal in ConanCenter during this migration process is to ensure
that recipes work with v1 and v2** and to make the transition as smooth as
possible for contributors and users. In the end we will be providing 
working recipes and binaries for both versions.

This process will require a lot of work also in the internals, we will keep
communicating those changes and the relevant updates in the 
[changelog](changelog.md). Here there are the main steps that we are
planning for the following months.

## Short term

### Prepare the CI infrastructure

Workers for Conan v2 will be ready for Windows, Macos and Linux alternatives. 
[Modern docker images](https://github.com/conan-io/conan-docker-tools/tree/master/modern) with Conan v2 are already 
available to use, for example `conanio/gcc11-ubuntu16.04:2.0.0-pre`. 
Note that we will be using tag name `2.0.0-pre` until there is an
actual Conan v2 release, this tag will use the latest pre-release
available (alpha, beta or release candidate).

### Export recipes using Conan v2 (warning)

We will start to run `conan export` using Conan v2 and the result will be
added to the comments by the bot. Failing this command won't make the 
pull-request fail at this moment, but we expect contributors to start
gaining awareness about changes in Conan v2.

### Prepare a syntax linter (CCI specific)

We want to provide a Conan recipe's linter in this repository. We will add
warnings and errors to it following the pace dictated by the community.
The purpose is that this linter will fail pull-requests if there is any
error and, this way, we can start to migrate small (and easy) bits of 
recipes... and ensure that future pull-requests don't introduce
regressions.

This linter can (and surely will) implement some of the checks that are
being currently done by [hooks](https://github.com/conan-io/hooks), but
the purpose is not replace them:
* hooks are really useful from the CLI, and are easier to install and run.
* linter provides much better output in GitHub interface.

### Run an scheduled job exporting all recipes

The same way we [export all the recipes every night using Conan v1](https://github.com/conan-io/conan-center-index/issues/2232), we will
run something similar using Conan v2 and report the results to an issue in
this repository.

It will help us to know how many recipes are fixed at a given time and
think about efforts and impact of next steps.

## Mid term

### Add CI running Conan v2 (hidden)

We will start working on a CI running Conan v2. Once recipes start to be
exported successfully, next step is to start building the packages.

We are going to prepare the CI and start running it behind the scenes
(sorry, at this moment hidden to users) in order to understand and
experiment ourself some challenges that will come with Conan v2: syntax,
configuration defaults,...

### Show CI results to contributors (info)

Once the errors start to make sense, we will start to provide these outputs
in pull-requests (although successful builds using v2 won't be required to
merge). Again, we expect some contributors to be aware of these errors,
maybe try to fix those builds, and for sure report feedback.

### Linter - turn more warnings to errors

During all this time, the plan is to move linter warnings to errors, one
by one and taking into account the effort required to fix them. With the
help of the linter more recipes should start to work (just `conan export`)
using Conan v2.

### Export using Conan v2 becomes an error

When a significant number (TBD) of recipes start to be exported
successfully, we will turn those export warnings into actual errors and
they will be become required to merge the pull-requests

## Long term

### CI running v2 is reported (and required)

Next step is to start running and reporting the results of the builds using
v2 for all the configurations, like we do for Conan v1. At this time all
pull-requests need to work with v1 and v2 to be merged.

### Conan v2 remote

TBD. Packages built using Conan v2 will become available for users

### Webpage with v2 information

ConanCenter webpage will start to show relevant information related to v2
packages and, eventually, v2 information will be the only available.

## Future

After this process in completed, we will consider the deprecation and
decommission of the infrastructure to generate v1 packages.
