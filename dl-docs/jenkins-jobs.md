# Jenkins jobs

<!-- mdformat-toc start --slug=github --no-anchors --maxlevel=6 --minlevel=2 -->

- [Recipe uploads](#recipe-uploads)
  - [Forcing an upload of all recipes](#forcing-an-upload-of-all-recipes)
- [Nightly tool builds](#nightly-tool-builds)
  - [Requesting a full rebuild](#requesting-a-full-rebuild)
  - [Building individual tools](#building-individual-tools)
- [Merges from `conan-io/conan-center-index` to `develop`](#merges-from-conan-ioconan-center-index-to-develop)
  - [Controlling the interval of automated merges](#controlling-the-interval-of-automated-merges)
  - [Requesting a merge](#requesting-a-merge)
- [Merging `develop` to `master` to put recipes into production](#merging-develop-to-master-to-put-recipes-into-production)
  - [Criteria](#criteria)
  - [Performing the merge](#performing-the-merge)

<!-- mdformat-toc end -->

## Recipe uploads

Recipe uploads are done automatically on the `develop` and `master` branches
whenever the branch builds.

As an optimization, recipes are uploaded incrementally. The Jenkins job looks
for any recipe changes added to the branch in question:

1. ...since before the most recent merge commit of any kind to the branch.
2. ...in the last _two_ merges that ultimately came from `conan-io/master`, in
   other words, two updates worth of changes from `conan-io`.

For each package, every recipe version is exported and then the recipes are
uploaded to the appropriate repo:

| Branch    | Destination repo          |
| --------- | ------------------------- |
| `develop` | `conan-center-dl-staging` |
| `master`  | `conan-center-dl`         |

Conan will only upload the recipes if they've changed, based on a checksum of
the recipe. This saves time, and avoids removing packages that have been built
and cached.

### Forcing an upload of all recipes

If there is a lack of confidence in the incremental upload, it's possible to run
a job to upload _all_ the recipes. Even though recipes are generated and
uploaded in parallel, this could take more than 20 minutes, which is why the
optimization is normally used.

To force an upload of all recipes:

1. Go to the build page for the branch in question:
   [`develop`](http://kepler.dlogics.com:8080/job/Datalogics/job/conan-center-index/job/develop/build)
   or
   [`master`](http://kepler.dlogics.com:8080/job/Datalogics/job/conan-center-index/job/master/build).
2. Check the **UPLOAD_ALL_RECIPES** checkbox.
3. Click the **Build** button.

## Nightly tool builds

Every night, Jenkins runs pytest to do a build of the tools. The results of the
tool builds appear in the Jenkins run page, and in HTML files that are collected
as build artifacts.

The tests build the tools incrementally using `conan create`. If there were no
changes to cause the tool to build, the test package is built and run, verifying
that the cached tool at least runs.

If a tool build fails, check the HTML results. The full log of the build attempt
is in the HTML result file, and is segregated for each tool.

### Requesting a full rebuild

You can force a full rebuild of the tools. To do this:

1. Go to the build page for the branch in question:
   [`develop`](http://kepler.dlogics.com:8080/job/Datalogics/job/conan-center-index/job/develop/build)
   or
   [`master`](http://kepler.dlogics.com:8080/job/Datalogics/job/conan-center-index/job/master/build).
2. If you want to just build the tools, check the **FORCE_TOOL_BUILD** checkbox.
3. If you want to build the tools and also force the tools' _requirements_ to be
   built, check the **FORCE_TOOL_BUILD_WITH_REQUIREMENTS** checkbox. **Note:**
   This can take quite a while, as _all_ the requirements will be built for
   _each_ tool.
4. Click the **Build** button.

### Building individual tools

You can also force an individual tool to be rebuilt.

1. Go to the build page for the branch in question:
   [`develop`](http://kepler.dlogics.com:8080/job/Datalogics/job/conan-center-index/job/develop/build)
   or
   [`master`](http://kepler.dlogics.com:8080/job/Datalogics/job/conan-center-index/job/master/build).
2. In the **PYTEST_OPTIONS** field, enter `-k` followed by the name of the tool,
   i.e., for SWIG, add `-k swig`. What you're doing here is adding an option to
   the `pytest` command, asking to only run tests with the tool's name in the
   command. For more information on options for pytest, see
   [the pytest doc](https://docs.pytest.org/en/7.1.x/how-to/usage.html).
3. If you want to just build the tool, check the **FORCE_TOOL_BUILD** checkbox.
4. If you want to build the tool and also force the tool's _requirements_ to be
   built, check the **FORCE_TOOL_BUILD_WITH_REQUIREMENTS** checkbox. **Note:**
   This can take quite a while, as _all_ the requirements will be built for
   _each_ tool.
5. Click the **Build** button.

## Merges from `conan-io/conan-center-index` to `develop`

The nightly Jenkins run automatically retrieves changes from
`conan-io/conan-center-index`, by running the
[`merge-upstream`](merge-upstream.md) task. See that documentation page for the
details.

Normally, the merge runs without needing any attention. The task is set up to
automatically resolve merge conflicts where DL has overridden files from
`conan-io`, either deliberately, or by removing the files.

If the merge fails, the task will instead make a PR for the merge, and assign
and request reviews for that PR based on
[the configuration](merge-upstream.md#configuration) in `dlproject.yaml`.

### Controlling the interval of automated merges

Currently, the upstream merge happens nightly. This is done by setting the
parameter `MERGE_UPSTREAM=true` for the develop branch in the `Jenkinsfile`:

```groovy
    triggers {
        // From the doc: @midnight actually means some time between 12:00 AM and 2:59 AM.
        // This gives us automatic spreading out of jobs, so they don't cause load spikes.
        parameterizedCron(env.BRANCH_NAME =~ 'develop' ? '@midnight % MERGE_UPSTREAM=true' : '@midnight')
    }
```

The interval could be changed; for instance, there could be one
`parameterizedCron` statement to run the nightlies every night between midnight
and 3 AM, and another `parameterizedCron` statement to run the `develop` branch
with the `MERGE_UPSTREAM=true` parameter at 3:30 AM Saturday morning. The
following example should work, but has not been tested.

```groovy
    triggers {
        // From the doc: @midnight actually means some time between 12:00 AM and 2:59 AM.
        // This gives us automatic spreading out of jobs, so they don't cause load spikes.
        parameterizedCron(env.BRANCH_NAME =~ 'develop'
            ? '''
                @midnight
                30 3 * * 6 % MERGE_UPSTREAM=true
              '''
            : '@midnight')
    }
```

### Requesting a merge

One might want to get recent recipe changes from `conan-io`, perhaps after an
important bugfix gets merged. To request an upstream merge manually:

1. Go to the
   [build page](http://kepler.dlogics.com:8080/view/All%20branches/job/Datalogics/job/conan-center-index/job/develop/build)
   in Jenkins for the `develop` branch.
2. Check the **MERGE_UPSTREAM** checkbox.
3. Click the **Build** button.

The upstream merge will run, followed by a job that uploads the recipes to the
staging repo and builds the tools.

## Merging `develop` to `master` to put recipes into production

Merging the `develop` branch of the Curated Conan Center Index to `master` puts
recipes into production, where they will be used by everyday builds in the
company.

The action is automatic, though the choice to take that action is one that is
manually made.

### Criteria

The choice to put recipes into production should be made by testing
representative projects against the `conan-center-dl-staging` repo, using the
techniques in
[Building against the staging repository](using-the-ccci-repositories.md#building-against-the-staging-repository).

Building those projects is done outside the `conan-center-index` job system, and
is outside the scope of this documentation.

### Performing the merge

1. Go to the
   [build page](http://kepler.dlogics.com:8080/view/All%20branches/job/Datalogics/job/conan-center-index/job/master/build)
   in Jenkins for the `master` branch.
2. Check the **MERGE_STAGING_TO_PRODUCTION** checkbox.
3. Click the **Build** button.
