# conan-center-index

This is the Datalogics fork of
[conan-io/conan-center-index](https://github.com/conan-io/conan-center-index).

It contains curated branches, and Datalogics-local modifications of recipes.

It also has Invoke tasks and CI implementations that:

- Upload recipes to our own repositories on Artifactory.
- Pre-build tools with specific profiles and upload them to Artifactory.

## DL Documentation

### Configuration and daily operations

- [Using the Curated Conan Center Index Conan repositories](dl-docs/using-the-ccci-repositories.md)
  - [Building against the staging repository](dl-docs/using-the-ccci-repositories.md#building-against-the-staging-repository)
  - [Using standard build profiles](dl-docs/using-the-ccci-repositories.md#using-standard-build-profiles)
- [Updating a recipe](dl-docs/updating-a-recipe.md)
  - [Adding a new revision of a recipe](dl-docs/updating-a-recipe.md#adding-a-new-revision-of-a-recipe)
    - [In conjunction with a contribution to `conan-io/conan-center-index`](dl-docs/updating-a-recipe.md#in-conjunction-with-a-contribution-to-conan-ioconan-center-index)
    - [At DL only](dl-docs/updating-a-recipe.md#at-dl-only)
  - [Testing the updated recipe with DL projects](dl-docs/updating-a-recipe.md#testing-the-updated-recipe-with-dl-projects)
  - [Bringing updates to production](dl-docs/updating-a-recipe.md#bringing-updates-to-production)
- [Specifying automatic builds of tools](dl-docs/automatic-tool-builds.md)
  - [Configurations for tools](dl-docs/automatic-tool-builds.md#configurations-for-tools)
    - [Standard build profiles](dl-docs/automatic-tool-builds.md#standard-build-profiles)
    - [Using specific compilers](dl-docs/automatic-tool-builds.md#using-specific-compilers)
  - [Specifying which tools to build](dl-docs/automatic-tool-builds.md#specifying-which-tools-to-build)
    - [Using a dictionary](dl-docs/automatic-tool-builds.md#using-a-dictionary)
      - [Limiting which tool configs to use](dl-docs/automatic-tool-builds.md#limiting-which-tool-configs-to-use)
      - [Specifying options for building the tool](dl-docs/automatic-tool-builds.md#specifying-options-for-building-the-tool)
    - [Using version ranges](dl-docs/automatic-tool-builds.md#using-version-ranges)
    - [Configurations for tools](dl-docs/automatic-tool-builds.md#configurations-for-tools)
      - [Standard build profiles](dl-docs/automatic-tool-builds.md#standard-build-profiles)
      - [Using specific compilers](dl-docs/automatic-tool-builds.md#using-specific-compilers)
  - [Using version ranges](dl-docs/automatic-tool-builds.md#using-version-ranges)
- [Jenkins jobs](dl-docs/jenkins-jobs.md)
  - [Recipe uploads](dl-docs/jenkins-jobs.md#recipe-uploads)
    - [Forcing an upload of all recipes](dl-docs/jenkins-jobs.md#forcing-an-upload-of-all-recipes)
  - [Nightly tool builds](dl-docs/jenkins-jobs.md#nightly-tool-builds)
    - [Requesting a full rebuild](dl-docs/jenkins-jobs.md#requesting-a-full-rebuild)
    - [Building individual tools](dl-docs/jenkins-jobs.md#building-individual-tools)
  - [Merges from `conan-io/conan-center-index` to `develop`](dl-docs/jenkins-jobs.md#merges-from-conan-ioconan-center-index-to-develop)
    - [Controlling the interval of automated merges](dl-docs/jenkins-jobs.md#controlling-the-interval-of-automated-merges)
    - [Requesting a merge](dl-docs/jenkins-jobs.md#requesting-a-merge)
  - [Merging `develop` to `master` to put recipes into production](dl-docs/jenkins-jobs.md#merging-develop-to-master-to-put-recipes-into-production)
    - [Criteria](dl-docs/jenkins-jobs.md#criteria)
    - [Performing the merge](dl-docs/jenkins-jobs.md#performing-the-merge)

### Troubleshooting

- [Analyzing build failures](dl-docs/troubleshooting.md#analyzing-build-failures)
- [Using pytest to run the tools builders](dl-docs/troubleshooting.md#using-pytest-to-run-the-tools-builders)
- [Resolving merge conflicts from the upstream repo](dl-docs/troubleshooting.md#resolving-merge-conflicts-from-the-upstream-repo)
- [Requesting a full build of the tools and their requirements](dl-docs/jenkins-jobs.md#requesting-a-full-rebuild)
- [Requesting a full (non-incremental) recipe upload](dl-docs/jenkins-jobs.md#forcing-an-upload-of-all-recipes)

### Reference

- [`merge-upstream` task](dl-docs/merge-upstream.md)
  - [Automatically Resolved Merge Conflicts](dl-docs/auto-merge-conflict-resolution.md)
- [`merge-staging-to-production` task](dl-docs/merge-staging-to-production.md)
