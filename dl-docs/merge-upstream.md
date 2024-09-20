# `merge-upstream` task

The `invoke merge-upstream` task fetches the latest `master` branch from the
[`conan-io/conan-center-index`](https://github.com/conan-io/conan-center-index)
repository, and merges it into the `develop` branch.

<!-- mdformat-toc start --slug=github --no-anchors --maxlevel=6 --minlevel=2 -->

- [Operation](#operation)
  - [Nuances](#nuances)
- [Configuration](#configuration)
- [When it runs](#when-it-runs)
- [See also](#see-also)

<!-- mdformat-toc end -->

## Operation

1. Check for preconditions: The repository is not dirty, the `gh`
   [GitHub CLI](https://cli.github.com/) command is installed, and the `gh`
   command is logged in to Octocat.
2. Fetch the `master` branch from `conan-io/conan-center-index`.
3. Attempt to merge it into the `develop` branch, automatically resolving some
   merge conflicts in favor of Datalogics' changes as specified in
   `.gitattributes-merge`.
4. If there are any merge conflicts that resulted from the Conan project
   modifying files that Datalogics deleted, resolve those in favor of the
   Datalogics deletion. This means we can delete GitHub templates and the like,
   so they don't affect the way we use our fork.
5. If merge conflicts remain, create a pull request in the current user's fork,
   using a copy of the `master` branch at `conan-io/conan-center-index`. A
   developer will have to review and resolve the merge conflicts, and approve
   the PR. The assignee and reviewers for the pull request can be configured.
6. If there were no merge conflicts, then push the merge to the `develop`
   branch.

### Nuances

- If there is already a pull request due to a merge conflict, and
  `merge-upstream` discovers more new commits in `conan-io/conan-center-index`,
  then it updates the pull request instead of making a new one.
- The credentials in the Jenkins job are passed by setting `GH_ENTERPRISE_TOKEN`
  and `GH_HOST` in the environment. See the comment in the `Jenkinsfile` for how
  to make a token and store it in Kepler.

## Configuration

The configuration is controlled by the `merge_upstream` key in `dlproject.yaml`.
Any unspecified values will get the following defaults.

The defaults are:

```yaml
merge_upstream:
    cci:
        url: git@github.com:conan-io/conan-center-index.git
        branch: master
    upstream:
        host: octocat.dlogics.com
        organization: datalogics
        branch: develop
        remote_name: merge-upstream-remote
    pull_request:
        host: octocat.dlogics.com
        fork: <current username>
        merge_branch_name: merge-from-conan-io
        reviewers: [ ]
        assignee: null
        labels:
            - from-conan-io
```

One use of this would be to use a personal fork for testing, to avoid polluting
the Datalogics organization repo:

```yaml
merge_upstream:
    upstream:
        # Temporary overrides
        organization: kam
```

## When it runs

- When Jenkins builds the `develop` branch triggered by the `parameterizedCron`
  statement in the `triggers` section of the `Jenkinsfile`, when the
  `MERGE_UPSTREAM` parameter is set. As of this writing, the merge occurs
  nightly. There's enough flexibility in the Cron triggers to permit, for
  instance, only doing the merges on the weekends.
- By going to the `develop` branch of `conan-center-index` on Jenkins and doing
  a **Build with parameters**, and clicking the **MERGE_UPSTREAM** parameter.
- By invoking `invoke merge-upstream` from the command line. This should only be
  done when developing and testing; for everyday use, request the merge via
  Jenkins.

If Jenkins runs `invoke merge-upstream`, and the branch was successfully pushed,
it skips the rest of the job. Updating the `develop` branch will trigger a
following job with the new commits.

## See also

- [Automatically Resolved Merge Conflicts](auto-merge-conflict-resolution.md)
