# `merge-staging-to-production` task

The `invoke merge-upstream` task fetches the latest `master` branch from the
[`conan-io/conan-center-index`](https://github.com/conan-io/conan-center-index)
repository, and merges it into the `develop` branch.

<!-- mdformat-toc start --slug=github --no-anchors --maxlevel=6 --minlevel=2 -->

- [Operation](#operation)
- [Configuration](#configuration)
- [When it runs](#when-it-runs)

<!-- mdformat-toc end -->

## Operation

1. Check out the `master` branch from `datalogics/conan-center-index`.
2. Fetch the `develop` branch from `datalogics/conan-center-index`.
3. If there are any new changes on the `develop` branch, merge it into the
   `master` branch.
4. If there was a successful merge, push the `master` back up to the
   `datalogics/conan-center-index` repo.

Since there are no contributions to the `master` branch that doesn't come from
the `develop` branch, any merge conflicts are unexpected.

## Configuration

The configuration is controlled by the `merge-staging-to-production` key in
`dlproject.yaml`. Any unspecified values will get the following defaults.

The defaults are:

```yaml
merge_staging_to_production:
    host: octocat.dlogics.com
    organization: datalogics
    staging_branch: develop
    production_branch: master
```

One use of this would be to use a personal fork for testing, to avoid polluting
the Datalogics organization repo:

```yaml
merge_staging_to_production:
    # Temporary overrides
    organization: kam
```

## When it runs

A merge of staging to production is a manual task done only after proving that
the current staging repo (based on the `develop` branch) will build a set of
important projects.

- By going to the `master` branch of `conan-center-index` on Jenkins and doing a
  **Build with parameters**, and clicking the **MERGE_STAGING_TO_PRODUCTION**
  parameter.
- By invoking `invoke merge-staging-to-production` from the command line. This
  should only be done when developing and testing; for everyday use, request the
  merge via Jenkins.
